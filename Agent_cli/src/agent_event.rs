// event.rs

#[derive(Debug)]
pub enum AgentEvent {
    Reasoning(String),

    Content(String),

    ToolStart { tool: String, args: String },

    ToolResult(String),

    Finish,

    Error(String),
}

pub enum ChatChunk {
    User(String),

    Reasoning(String),

    Assistant(String),

    ToolCall { tool: String, args: String },

    ToolResult(String),

    Error(String),
}
