import streamlit as st
import json
from pydantic import BaseModel, Field
from typing import Optional
from movie_tool import get_tools, query_movie_db
from chart_tool import get_chart_tool, validate_chart


# ── State ──

DEFAULT_STATE = {
    "agent_phase": "idle",
    "agent_events": [],
    "agent_messages": [],
    "agent_tools": [],
    "agent_df": None,
    "agent_chart_specs": [],
    "agent_pending_message": None,
    "user_guidance": "",
    "guidance_level": "none",
    "analysis_focus": "",
    "preferred_tools": [],
}

def get_state(key):
    return st.session_state.get(key, DEFAULT_STATE[key])

def set_state(key, value):
    st.session_state[key] = value

def restart_agent(user_question, filtered_df, show_chart=False):
    set_state("agent_phase", "thinking")
    set_state("agent_events", [])
    set_state("agent_chart_specs", [])
    set_state("agent_pending_message", None)
    
    # Reset guidance state
    set_state("user_guidance", "")
    set_state("guidance_level", "none")
    set_state("analysis_focus", "")
    set_state("preferred_tools", [])

    tools = get_tools(filtered_df)
    system_content = "You are a data analyst with access to a tool that executes Python code on a movie database."
    
    # Add user guidance to system content
    guidance_level = get_state("guidance_level")
    user_guidance = get_state("user_guidance")
    analysis_focus = get_state("analysis_focus")
    preferred_tools = get_state("preferred_tools")
    
    if guidance_level != "none":
        system_content += "\n\nUser Guidance:\n"
        if user_guidance:
            system_content += f"General guidance: {user_guidance}\n"
        if analysis_focus:
            system_content += f"Focus areas: {analysis_focus}\n"
        if preferred_tools:
            system_content += f"Preferred approaches: {', '.join(preferred_tools)}\n"
        
        if guidance_level == "strong":
            system_content += "\nIMPORTANT: Follow the user guidance closely and prioritize their preferred approaches."
        elif guidance_level == "moderate":
            system_content += "\nConsider the user guidance as helpful suggestions but use your judgment."
        elif guidance_level == "light":
            system_content += "\nKeep the user guidance in mind as background context."

    if show_chart:
        tools.append(get_chart_tool())
        system_content += " After computing the data, create a chart using a Vega-Lite specification."

    set_state("agent_messages", [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_question},
    ])
    set_state("agent_tools", tools)
    set_state("agent_df", filtered_df)


def update_guidance(guidance, level, focus, tools):
    set_state("user_guidance", guidance)
    set_state("guidance_level", level)
    set_state("analysis_focus", focus)
    set_state("preferred_tools", tools)
    
    # If agent is already running, update the system message
    if get_state("agent_phase") != "idle":
        messages = get_state("agent_messages")
        # Update the system message with new guidance
        system_content = "You are a data analyst with access to a tool that executes Python code on a movie database."
        
        if level != "none":
            system_content += "\n\nUser Guidance:\n"
            if guidance:
                system_content += f"General guidance: {guidance}\n"
            if focus:
                system_content += f"Focus areas: {focus}\n"
            if tools:
                system_content += f"Preferred approaches: {', '.join(tools)}\n"
            
            if level == "strong":
                system_content += "\nIMPORTANT: Follow the user guidance closely and prioritize their preferred approaches."
            elif level == "moderate":
                system_content += "\nConsider the user guidance as helpful suggestions but use your judgment."
            elif level == "light":
                system_content += "\nKeep the user guidance in mind as background context."
        
        # Update the first message (system message)
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = system_content
            set_state("agent_messages", messages)

# ── Logic ──

def run_step(client):
    phase = get_state("agent_phase")
    messages = get_state("agent_messages")

    if phase == "thinking":
        class Reasoning(BaseModel):
            reason: str = Field(description="Your reasoning about what you know so far and what to do next")
            use_tool: bool = Field(description="True if you need to run code or create a chart, False if you can give the final answer")
            answer: Optional[str] = Field(default=None, description="Your final answer in one short paragraph. Only provide when use_tool is False.")

        response = client.chat.completions.parse(
            model="gpt-4o-mini", messages=messages, response_format=Reasoning,
        )
        reasoning = response.choices[0].message.parsed
        messages.append({"role": "assistant", "content": reasoning.reason})

        if reasoning.use_tool:
            get_state("agent_events").append({"type": "thought", "thought": reasoning.reason})
            set_state("agent_phase", "acting")
        else:
            get_state("agent_events").append({"type": "answer", "thought": reasoning.reason, "answer": reasoning.answer})
            set_state("agent_phase", "done")

    elif phase == "acting":
        tools = get_state("agent_tools")

        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools, parallel_tool_calls=False,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            set_state("agent_phase", "done")
            return

        set_state("agent_pending_message", msg)
        set_state("agent_phase", "awaiting_approval")

def execute_pending_tools():
    messages = get_state("agent_messages")
    df = get_state("agent_df")
    pending_msg = get_state("agent_pending_message")

    messages.append(pending_msg)
    for tc in pending_msg.tool_calls:
        args = json.loads(tc.function.arguments)

        if tc.function.name == "QueryMovieDB":
            result = query_movie_db(args["code"], df)
            get_state("agent_events").append({
                "type": "action", "name": tc.function.name,
                "code": args["code"], "result": result,
            })
        elif tc.function.name == "CreateChart":
            spec, result = validate_chart(args["vega_lite_spec"])
            if spec:
                get_state("agent_chart_specs").append(spec)
            get_state("agent_events").append({
                "type": "chart", "name": tc.function.name,
                "spec_str": args["vega_lite_spec"], "result": result,
            })

        messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})

    set_state("agent_pending_message", None)
    set_state("agent_phase", "thinking")

def reject_pending_tools(feedback):
    messages = get_state("agent_messages")
    pending_msg = get_state("agent_pending_message")

    rejection_msg = "User rejected this action."
    if feedback:
        rejection_msg += f" User feedback: {feedback}"
    else:
        rejection_msg += " Try a different approach."

    messages.append(pending_msg)
    for tc in pending_msg.tool_calls:
        get_state("agent_events").append({
            "type": "rejected", "name": tc.function.name,
            "feedback": feedback,
        })
        messages.append({"role": "tool", "content": rejection_msg, "tool_call_id": tc.id})

    set_state("agent_pending_message", None)
    set_state("agent_phase", "thinking")


# ── Rendering ──

def render_guidance_panel():
    """Render the guidance control panel"""
    st.subheader("🧭 Agent Guidance")
    
    # Guidance level selector
    guidance_level = get_state("guidance_level")
    new_level = st.selectbox(
        "Guidance Level:",
        options=["none", "light", "moderate", "strong"],
        index=["none", "light", "moderate", "strong"].index(guidance_level),
        help="How much should the agent follow your guidance?"
    )
    
    # General guidance text
    current_guidance = get_state("user_guidance")
    new_guidance = st.text_area(
        "General Guidance:",
        value=current_guidance,
        placeholder="E.g., 'Focus on statistical significance', 'Consider only recent movies', 'Be thorough but concise'",
        help="Provide general hints or constraints for the agent's analysis approach"
    )
    
    # Analysis focus
    current_focus = get_state("analysis_focus")
    new_focus = st.text_input(
        "Analysis Focus:",
        value=current_focus,
        placeholder="E.g., 'genre trends', 'rating patterns', 'temporal analysis'",
        help="Specific areas or aspects to focus on"
    )
    
    # Preferred approaches/tools
    current_tools = get_state("preferred_tools")
    tools_options = ["statistical analysis", "data visualization", "filtering", "aggregation", "comparison", "trend analysis"]
    new_tools = st.multiselect(
        "Preferred Approaches:",
        options=tools_options,
        default=current_tools if current_tools else [],
        help="Select analysis approaches you'd like the agent to prioritize"
    )
    
    # Apply guidance button
    col1, col2 = st.columns([1, 1])
    with col1:
        apply_guidance = st.button("Apply Guidance", type="primary", use_container_width=True)
    with col2:
        clear_guidance = st.button("Clear Guidance", use_container_width=True)
    
    # Handle guidance updates
    if apply_guidance:
        update_guidance(new_guidance, new_level, new_focus, new_tools)
        get_state("agent_events").append({
            "type": "guidance_update",
            "level": new_level,
            "guidance": new_guidance,
            "focus": new_focus,
            "tools": new_tools
        })
        st.rerun()
    
    if clear_guidance:
        update_guidance("", "none", "", [])
        get_state("agent_events").append({
            "type": "guidance_cleared"
        })
        st.rerun()
    
    # Show current guidance status
    if guidance_level != "none":
        st.info(f"📍 **Current Guidance Level:** {guidance_level.title()}")
        if new_guidance:
            st.write(f"💭 **Guidance:** {new_guidance}")
        if new_focus:
            st.write(f"🎯 **Focus:** {new_focus}")
        if new_tools:
            st.write(f"🛠️ **Preferred:** {', '.join(new_tools)}")

def render_events():
    for event in get_state("agent_events"):
        if event["type"] == "thought":
            st.markdown(f"**Thought:** {event['thought']}")
        elif event["type"] == "action":
            st.markdown(f"**Action:** `{event['name']}`")
            st.code(event["code"], language="python")
            st.markdown("**Observation:**")
            st.code(event["result"], language="text")
            st.divider()
        elif event["type"] == "chart":
            st.markdown(f"**Action:** `{event['name']}`")
            st.code(event["spec_str"], language="json")
            st.markdown("**Observation:**")
            st.code(event["result"], language="text")
            st.divider()
        elif event["type"] == "rejected":
            st.markdown(f"**Rejected:** `{event['name']}`")
            if event.get("feedback"):
                st.text(f"Feedback: {event['feedback']}")
            st.divider()
        elif event["type"] == "guidance_update":
            st.markdown(f"**🧭 Guidance Updated (Level: {event['level'].title()})**")
            if event.get("guidance"):
                st.write(f"💭 {event['guidance']}")
            if event.get("focus"):
                st.write(f"🎯 Focus: {event['focus']}")
            if event.get("tools"):
                st.write(f"🛠️ Approaches: {', '.join(event['tools'])}")
            st.divider()
        elif event["type"] == "guidance_cleared":
            st.markdown("**🧭 Guidance Cleared**")
            st.divider()
        elif event["type"] == "answer":
            st.markdown(f"**Thought:** {event['thought']}")

def render_pending_approval():
    st.warning("The agent wants to perform the following action:")
    for tc in get_state("agent_pending_message").tool_calls:
        args = json.loads(tc.function.arguments)
        st.markdown(f"**Tool:** `{tc.function.name}`")
        if tc.function.name == "QueryMovieDB":
            st.code(args["code"], language="python")
        elif tc.function.name == "CreateChart":
            st.code(args["vega_lite_spec"], language="json")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        approved = st.button("Approve", type="primary", use_container_width=True)
    with btn_col2:
        rejected = st.button("Reject", use_container_width=True)
    return approved, rejected

def render_pending_feedback():
    feedback = st.text_input(
        "Why are you rejecting? Tell the agent what to do instead:",
        key="reject_feedback",
    )
    submitted = st.button("Submit Rejection", use_container_width=True)
    return submitted, feedback

def render_panel():
    # Create a two-column layout: guidance panel on left, main content on right
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_guidance_panel()
    
    with col2:
        st.subheader("Analysis Results")
        container = st.container(height=600)
        actions = {}
        with container:
            phase = get_state("agent_phase")

            if phase == "idle":
                st.info("Enter a question and click 'Analyze' to see results.")

            elif phase in ("thinking", "acting"):
                with st.expander("Agent Reasoning Trace", expanded=True):
                    render_events()
                st.spinner("Agent is thinking...")

            elif phase == "awaiting_approval":
                with st.expander("Agent Reasoning Trace", expanded=True):
                    render_events()
                approved, rejected = render_pending_approval()
                actions = {"approved": approved, "rejected": rejected}

            elif phase == "awaiting_feedback":
                with st.expander("Agent Reasoning Trace", expanded=True):
                    render_events()
                submitted, feedback = render_pending_feedback()
                actions = {"submitted": submitted, "feedback": feedback}

            elif phase == "done":
                with st.expander("Agent Reasoning Trace", expanded=False):
                    render_events()
                events = get_state("agent_events")
                if events and events[-1].get("answer"):
                    st.write("**Answer:**")
                    st.write(events[-1]["answer"])
                for spec in get_state("agent_chart_specs"):
                    st.vega_lite_chart(spec, use_container_width=True)

    return actions


# ── Lifecycle ──

def agent_panel(client, analyze_button, user_question, filtered_df, show_chart=False):
    # Phases: idle -> thinking <-> acting -> awaiting_approval -> thinking ... -> done
    #                                     -> awaiting_feedback -> thinking ... -> done
    if analyze_button and user_question:
        restart_agent(user_question, filtered_df, show_chart)

    actions = render_panel()

    phase = get_state("agent_phase")
    if phase in ("thinking", "acting"):
        run_step(client)
        st.rerun()
    elif phase == "awaiting_approval":
        if actions.get("approved"):
            execute_pending_tools()
            st.rerun()
        elif actions.get("rejected"):
            set_state("agent_phase", "awaiting_feedback")
            st.rerun()
    elif phase == "awaiting_feedback" and actions.get("submitted"):
        reject_pending_tools(actions.get("feedback", ""))
        st.rerun()
