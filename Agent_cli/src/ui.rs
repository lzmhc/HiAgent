use crate::{event::ChatChunk, app::App};
use ratatui::layout::Rect;
/// Helpers for drawing the TUI layout.
use ratatui::widgets::Wrap;
use unicode_width::UnicodeWidthChar;
use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Paragraph, Scrollbar, ScrollbarOrientation},
};

pub fn draw(frame: &mut Frame, app: &mut App) {
    let layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(2), // Header
            Constraint::Min(1),    // Chat
            Constraint::Length(5), // Input
            Constraint::Length(1), // Footer
        ])
        .split(frame.area());

    draw_header(frame, layout[0], app);

    draw_chat(frame, layout[1], app);

    draw_input(frame, layout[2], app);

    draw_footer(frame, layout[3]);
}

fn draw_header(frame: &mut Frame, area: ratatui::layout::Rect, app: &App) {
    let title = if let Some(status) = &app.status {
        format!(
            "🤖 {}  Model:{}  Reason:{}  Workspace:{}",
            status.name, status.model, status.model_reasoning_effort, status.workspace
        )
    } else {
        "🤖Loading...".to_string()
    };
    let header = Paragraph::new(title)
        .style(
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        )
        .block(Block::default().borders(Borders::BOTTOM));
    frame.render_widget(header, area);
}

fn draw_chat(frame: &mut Frame, area: Rect, app: &mut App) {
    let mut text = Text::default();

    for block in &app.blocks {
        let rendered = match block {
            ChatChunk::User(msg) => {
                text.lines.push(Line::from(vec![
                    Span::styled("👤 ", Style::default().fg(Color::Green)),
                    Span::raw(msg),
                ]));
                true
            }

            ChatChunk::Reasoning(msg) => {
                if app.show_reasoning {
                    text.lines.push(Line::from(vec![
                        Span::styled("💭 ", Style::default().fg(Color::DarkGray)),
                        Span::styled(
                            msg.as_str(),
                            Style::default()
                                .fg(Color::DarkGray)
                                .add_modifier(Modifier::ITALIC),
                        ),
                    ]));
                } else {
                    text.lines.push(Line::from(vec![
                        Span::styled("💭 ", Style::default().fg(Color::DarkGray)),
                        Span::styled(
                            "推理过程已折叠",
                            Style::default()
                                .fg(Color::DarkGray)
                                .add_modifier(Modifier::ITALIC),
                        ),
                    ]));
                }
                true
            }

            ChatChunk::Assistant(msg) => {
                let lines: Vec<&str> = msg.lines().collect();
                if lines.is_empty() {
                    text.lines.push(Line::from(vec![
                        Span::styled("🤖 ", Style::default().fg(Color::Cyan)),
                    ]));
                } else {
                    text.lines.push(Line::from(vec![
                        Span::styled("🤖 ", Style::default().fg(Color::Cyan)),
                        Span::raw(lines[0]),
                    ]));
                    for line in &lines[1..] {
                        text.lines.push(Line::from(vec![
                            Span::raw("   "),
                            Span::raw(*line),
                        ]));
                    }
                }
                true
            }

            ChatChunk::ToolCall { name, args } => {
                text.lines.push(Line::from(vec![
                    Span::styled("🔧 ", Style::default().fg(Color::Yellow)),
                    Span::raw(format!("{name}({args})")),
                ]));
                true
            }

            ChatChunk::ToolResult { .. } => {
                false
            }

            ChatChunk::Error(err) => {
                text.lines.push(Line::from(vec![
                    Span::styled("❌ ", Style::default().fg(Color::Red)),
                    Span::raw(err),
                ]));
                true
            }
        };

        if rendered {
            text.lines.push(Line::default());
        }
    }

    let chat = Paragraph::new(text)
        .scroll((app.scroll, 0))
        .wrap(Wrap { trim: false });
    frame.render_widget(chat, area);
    let scrollbar = Scrollbar::new(ScrollbarOrientation::VerticalRight);
    frame.render_stateful_widget(scrollbar, area, &mut app.scrollbar);
}

fn draw_input(frame: &mut Frame, area: Rect, app: &App) {
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(Color::Cyan))
        .title(" 输入 ")
        .title_style(
            Style::default()
                .fg(Color::Yellow)
                .add_modifier(Modifier::BOLD),
        );

    let input_text = app.input.as_str().to_string();

    let input = Paragraph::new(input_text)
        .style(Style::default().fg(Color::White))
        .wrap(Wrap { trim: false })
        .block(block.clone());

    let inner_area = block.inner(area);
    frame.render_widget(input, area);

    let cursor_x = inner_area.x + app.input.chars()
        .map(|c| c.width().unwrap_or(0) as u16)
        .sum::<u16>();
    let cursor_y = inner_area.y;

    frame.set_cursor_position((cursor_x, cursor_y));
}

fn draw_footer(frame: &mut Frame, area: ratatui::layout::Rect) {
    let footer = Paragraph::new("Ctrl+R Reasoning  Ctrl+Q Exit").style(Style::default().fg(Color::DarkGray));

    frame.render_widget(footer, area);
}
