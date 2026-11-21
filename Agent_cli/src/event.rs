
#[derive(Debug)]
pub enum AgentEvent {
    User {
        content: String,
    },
    Assistant {
        content: String,
    },
    Reasoning {
        content: String,
    },
    Content {
        content: String,
    },
    Reason {
        content: String,
    },
    ToolCall {
        id: String,
        name: String,
        args: String,
    },
    ToolResult {
        content: String,
        tool_call_id: String
    },
    Stop,
    Error {
        content: String,
    },
}