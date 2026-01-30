#!/usr/bin/env python3
"""
Minimal demo of the Gradio interface without dependencies.
Shows the UI structure and Force Retrieval toggle.
"""
import gradio as gr


def demo_simple_chat(message, history):
    """Demo simple LLM chat (no retrieval)."""
    response = f"[SIMPLE LLM MODE] You asked: {message}\n\n" \
               "This would be a direct LLM response without searching documents. " \
               "Fast and conversational."
    history.append([message, response])
    return history, ""


def demo_rag_chat(message, history):
    """Demo RAG chat (with retrieval)."""
    response = f"[RAG MODE] You asked: {message}\n\n" \
               "Based on your research papers:\n\n" \
               "**Answer:** This would be a detailed answer synthesized from retrieved documents.\n\n" \
               "**Sources:**\n" \
               "- [1] Paper Title A (Smith et al., 2024) - Score: 0.89\n" \
               "- [2] Paper Title B (Jones et al., 2023) - Score: 0.85\n" \
               "- [3] Paper Title C (Brown et al., 2024) - Score: 0.82"
    history.append([message, response])
    return history, ""


def handle_demo_message(message, history, force_retrieval):
    """Route to appropriate chat mode."""
    if not message.strip():
        return history, ""
    
    if force_retrieval:
        return demo_rag_chat(message, history)
    else:
        return demo_simple_chat(message, history)


def create_demo_interface():
    """Create demo Gradio interface."""
    
    with gr.Blocks(title="Research RAG Assistant - Demo") as demo:
        
        gr.Markdown(
            """
            # 📚 Research RAG Assistant (Demo)
            
            **Force Retrieval OFF**: Simple LLM chat (fast, no document search)  
            **Force Retrieval ON**: Full RAG with document retrieval and citations
            """
        )
        
        with gr.Row():
            with gr.Column(scale=3):
                # Force Retrieval Toggle - PROMINENT
                force_retrieval = gr.Checkbox(
                    label="🔍 Force Retrieval",
                    value=False,
                    info="Enable to search documents and get cited answers. Disable for faster, simple chat.",
                )
                
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your message",
                        placeholder="Ask a question...",
                        scale=4,
                        lines=2
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                model_dropdown = gr.Dropdown(
                    choices=["llama-70b-chat", "mistral-7b", "qwen-14b"],
                    value="llama-70b-chat",
                    label="🤖 Model"
                )
                
                with gr.Accordion("📊 Retrieval Settings", open=True):
                    num_docs = gr.Slider(1, 20, 5, step=1, label="Number of Documents")
                    threshold = gr.Slider(50, 100, 75, step=5, label="Relevance Threshold (%)")
                
                gr.Markdown("---")
                gr.Markdown("### 📊 System Status")
                
                status = gr.Textbox(
                    value="✅ Demo mode - showing UI structure",
                    label="Status",
                    interactive=False,
                    lines=3
                )
        
        # Event handlers
        submit_btn.click(
            handle_demo_message,
            inputs=[msg, chatbot, force_retrieval],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            handle_demo_message,
            inputs=[msg, chatbot, force_retrieval],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(lambda: [], outputs=[chatbot])
        
        gr.Markdown(
            """
            ---
            
            **Tip**: Toggle Force Retrieval to see different modes!  
            - OFF: Simple LLM chat (fast)
            - ON: RAG with document search (cited answers)
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = create_demo_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
