mod event;
mod api;
mod app;
mod ui;

use crate::event::{AgentEvent, ChatChunk};
use app::App;
use crossterm::{
    event::{self as ct_event, Event, KeyCode, KeyModifiers},
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use ratatui::{Terminal, backend::CrosstermBackend};
use std::{io, sync::mpsc, time::Duration};
fn main() {
    if let Err(err) = run() {
        let _ = disable_raw_mode();
        let _ = execute!(io::stdout(), LeaveAlternateScreen);
        eprintln!("{err:#}");
        std::process::exit(1);
    }
}

fn run() -> color_eyre::eyre::Result<()> {
    color_eyre::install()?;

    enable_raw_mode()?;

    let mut stdout = io::stdout();

    execute!(stdout, EnterAlternateScreen)?;

    let backend = CrosstermBackend::new(stdout);

    let mut terminal = Terminal::new(backend)?;

    let mut app = App::new();

    {
        let rt = tokio::runtime::Runtime::new()?;
        match rt.block_on(api::fetch_status()) {
            Ok(status) => {
                app.status = Some(status);
            }
            Err(e) => {
                eprintln!("Failed to fetch status: {e}");
            }
        }
        match rt.block_on(api::start_new_session()) {
            Ok(session_id) => {
                app.current_session_id = session_id;
            }
            Err(e) => {
                eprintln!("Failed to fetch session_id: {e}");
            }
        }
    }

    let (tx, rx) = mpsc::channel::<AgentEvent>();
    loop {
        while let Ok(event) = rx.try_recv() {
            app.handle_agent_event(event);
        }
        terminal.draw(|f| {
            ui::draw(f, &mut app);
        })?;
        if ct_event::poll(Duration::from_millis(16))? {
            if let Event::Key(key) = ct_event::read()? {
                match key.code {
                    // ctrl+q 退出
                    KeyCode::Char('q') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                        break;
                    }
                    // ctrl+r 切换推理过程显示
                    KeyCode::Char('r') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                        app.toggle_reasoning();
                    }
                    // ctrl+l 会话列表切换
                    KeyCode::Char('l') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                        if !app.show_session_popup {
                            // 显示会话列表时，先获取会话列表
                            let rt = tokio::runtime::Runtime::new()?;
                            match rt.block_on(api::fetch_sessions()) {
                                Ok(sessions) => {
                                    app.update_sessions(sessions);
                                }
                                Err(e) => {
                                    eprintln!("Failed to fetch sessions: {e}");
                                }
                            }
                        }
                        app.toggle_session();
                    }

                    // 当会话列表显示时，处理会话列表的键盘导航
                    KeyCode::Up if app.show_session_popup => {
                        app.session_list_prev();
                    }

                    KeyCode::Down if app.show_session_popup => {
                        app.session_list_next();
                    }

                    KeyCode::Enter if app.show_session_popup => {
                        if let Some(session_id) = app.select_current_session() {
                            // 加载选中会话的历史记录
                            let tx = tx.clone();
                            let session_id_clone = session_id.clone();
                            std::thread::spawn(move || {
                                let rt = tokio::runtime::Runtime::new().unwrap();
                                rt.block_on(async {
                                    match api::fetch_session_history(session_id_clone).await {
                                        Ok(history) => {
                                            // 发送历史记录事件
                                            for chunk in history {
                                                let event = match chunk {
                                                    ChatChunk::User(msg) => AgentEvent::Content(msg),
                                                    ChatChunk::Assistant(msg) => AgentEvent::Content(msg),
                                                    _ => continue,
                                                };
                                                let _ = tx.send(event);
                                            }
                                        }
                                        Err(e) => {
                                            eprintln!("Failed to fetch session history: {e}");
                                        }
                                    }
                                });
                            });
                        }
                    }

                    KeyCode::Esc if app.show_session_popup => {
                        app.close_session_popup();
                    }

                    // 当会话列表不显示时，处理普通输入
                    KeyCode::Char(c) => {
                        app.insert_char(c);
                    }

                    KeyCode::Backspace => {
                        app.backspace();
                    }

                    KeyCode::Enter => {
                        let prompt = app.input.clone();
                        let session_id = app.current_session_id.clone();
                        
                        if prompt.trim().is_empty() {
                            continue;
                        }
                        app.blocks.push(ChatChunk::User(prompt.clone()));
                        let tx = tx.clone();
                        std::thread::spawn(move || {
                            let rt = tokio::runtime::Runtime::new().unwrap();
                            rt.block_on(async {
                                if let Err(e) = api::chat(prompt, session_id, tx).await {
                                    eprintln!("{e}");
                                }
                            });
                        });
                        app.clear();
                    }
                    KeyCode::Up => {
                        app.scroll = app.scroll.saturating_sub(1);
                    }

                    KeyCode::Down => {
                        app.scroll += 1;

                        app.scrollbar = app.scrollbar.position(app.scroll as usize);
                    }
                    KeyCode::Esc => {
                        app.clear();
                    }

                    _ => {}
                }
            }
        }
    }

    disable_raw_mode()?;

    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;

    terminal.show_cursor()?;

    Ok(())
}
