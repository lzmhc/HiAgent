
#[derive(Debug)]
pub enum AgentEvent {
    Content(String),
    Reason(String),
    ToolCall {
        id: String,
        name: String,
        args: String,
    },
    ToolResult {
        name: String,
        content: String,
    },
    Stop,
    Error(String),
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
