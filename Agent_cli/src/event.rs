
#[derive(Debug)]
pub enum AgentEvent {
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
        tool_call_id: String,
        name: String,
    },
    Stop,
    Error {
        content: String,
    },
}

#[derive(Debug)]
pub enum ChatChunk {
    User(String),
    Assistant(String),
    Reasoning(String),
    ToolCall { name: String, args: String },
    ToolResult { name: String, content: String },
    Error(String),
}
