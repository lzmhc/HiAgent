use ratatui::{
    Frame, layout::{Constraint,Direction,Layout,}, style::{Color,Modifier,Style,}, text::{Line, Span, Text}, widgets::{Block, BorderType, Borders, Paragraph, Scrollbar, ScrollbarOrientation},
};
use ratatui::widgets::Wrap;
use ratatui::layout::Rect;
use crate::{agent_event::ChatChunk, app::App};

pub fn draw(frame: &mut Frame, app: &mut App) {
    let layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Header
            Constraint::Min(1),    // Chat
            Constraint::Length(5), // Input
            Constraint::Length(1), // Footer
        ])
        .split(frame.area());

    draw_header(frame, layout[0]);

    draw_chat(frame, layout[1], app);

    draw_input(frame, layout[2], app);

    draw_footer(frame, layout[3]);
}

fn draw_header(frame: &mut Frame, area: ratatui::layout::Rect) {
    let header = Paragraph::new(
        "🤖 AgentBot    Model: qwen3-235b    Workspace: ~/project",
    )
    .style(
        Style::default()
            .fg(Color::Cyan)
            .add_modifier(Modifier::BOLD),
    )
    .block(
        Block::default()
            .borders(Borders::BOTTOM),
    );
    frame.render_widget(header, area);
}

fn draw_chat(frame: &mut Frame, area: Rect, app: &mut App) {
    let mut text = Text::default();

    for block in &app.blocks {
        match block {
            ChatChunk::User(msg) => {
                text.lines.push(Line::from(vec![
                    Span::styled("👤 ", Style::default().fg(Color::Green)),
                    Span::raw(msg),
                ]));
            }

            ChatChunk::Reasoning(msg) => {
                text.lines.push(Line::from(vec![
                    Span::styled("💭 ", Style::default().fg(Color::DarkGray)),
                    Span::raw(msg),
                ]));
            }

            ChatChunk::Assistant(msg) => {
                text.lines.push(Line::from(vec![
                    Span::styled("🤖 ", Style::default().fg(Color::Cyan)),
                    Span::raw(msg),
                ]));
            }

            ChatChunk::ToolCall { tool, args } => {
                text.lines.push(Line::from(vec![
                    Span::styled("🔧 ", Style::default().fg(Color::Yellow)),
                    Span::raw(format!("{tool} {args}")),
                ]));
            }

            ChatChunk::ToolResult(result) => {
                text.lines.push(Line::from(vec![
                    Span::styled("📄 ", Style::default().fg(Color::Magenta)),
                    Span::raw(result),
                ]));
            }

            ChatChunk::Error(err) => {
                text.lines.push(Line::from(vec![
                    Span::styled("❌ ", Style::default().fg(Color::Red)),
                    Span::raw(err),
                ]));
            }
        }

        // 每个聊天块之间留一个空行
        text.lines.push(Line::default());
    }

    let chat = Paragraph::new(text)
        .scroll((app.scroll, 0))
        .wrap(Wrap { trim: false });
        frame.render_widget(chat, area);
        let scrollbar = Scrollbar::new(ScrollbarOrientation::VerticalRight);
        frame.render_stateful_widget(
            scrollbar,
            area,
            &mut app.scrollbar,
        );
    }

fn draw_input(frame: &mut Frame, area: Rect, app: &App) {
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(Color::Cyan))
        .title(" 输入 ")
        .title_style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD));

    let input_text = format!("{}", app.input.as_str());
    
    let input = Paragraph::new(input_text)
        .style(Style::default().fg(Color::White))
        .wrap(Wrap { trim: false })
        .block(block.clone());

    let inner_area = block.inner(area);
    frame.render_widget(input, area);

    let cursor_x = inner_area.x + 3 + app.input.len() as u16;
    let cursor_y = inner_area.y;
    
    frame.set_cursor_position((cursor_x, cursor_y));
}

fn draw_footer(frame: &mut Frame, area: ratatui::layout::Rect) {
    let footer = Paragraph::new(
        "Ctrl+Q Exit",
    )
    .style(Style::default().fg(Color::DarkGray));

    frame.render_widget(footer, area);
}
