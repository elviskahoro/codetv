from __future__ import annotations

import reflex as rx
import asyncio
from typing import List, Dict, Any

PROCESS_STEPS = [
    {"id": 1, "name": "Initializing Agent", "description": "Setting up AI agent and tools"},
    {"id": 2, "name": "Processing URL", "description": "Fetching and parsing awesome list content"},
    {"id": 3, "name": "Analyzing Resources", "description": "Categorizing and evaluating learning resources"},
    {"id": 4, "name": "Generating Learning Paths", "description": "Creating personalized learning pathways"},
    {"id": 5, "name": "Finalizing Output", "description": "Preparing results and recommendations"}
]

class ProcessingState(rx.State):
    """State management for the CodeTV frontend application."""
    
    # Processing state
    current_step: int = 0
    is_processing: bool = False
    is_complete: bool = False
    
    # Input and output
    url_input: str = ""
    processing_results: Dict[str, Any] = {}
    error_message: str = ""
    
    # Demo data (since we're not connecting to backend)
    demo_results: Dict[str, Any] = {
        "status": "success",
        "parsed_data": {
            "topic": "Python Programming",
            "description": "A curated list of awesome Python frameworks, libraries, and resources",
            "language": "Python",
            "total_items": 342,
            "categories": [
                "Web Frameworks", "Data Science", "Machine Learning", 
                "Testing", "DevOps", "GUI Development", "Databases",
                "Networking", "Security", "Performance"
            ]
        },
        "learning_guidance": {
            "topic_summary": "Python is a versatile programming language perfect for beginners and experts alike.",
            "recommended_starting_point": "Start with Python basics, then move to web frameworks like Flask or Django",
            "learning_paths": [
                {
                    "name": "Python Fundamentals",
                    "difficulty": "Beginner",
                    "estimated_hours": 40,
                    "resources_count": 15,
                    "prerequisites": ["Basic programming concepts"],
                    "learning_objectives": ["Master Python syntax", "Understand OOP concepts"]
                },
                {
                    "name": "Web Development with Python",
                    "difficulty": "Intermediate",
                    "estimated_hours": 60,
                    "resources_count": 25,
                    "prerequisites": ["Python basics", "HTML/CSS knowledge"],
                    "learning_objectives": ["Build web applications", "Database integration"]
                }
            ]
        }
    }
    
    def set_url_input(self, value: str):
        """Update the URL input field."""
        self.url_input = value
    
    async def start_processing(self):
        """Simulate the processing workflow."""
        if not self.url_input.strip():
            self.error_message = "Please enter a valid Awesome List URL"
            return
        
        self.error_message = ""
        self.is_processing = True
        self.is_complete = False
        self.current_step = 0
        
        # Simulate processing steps
        for step in range(len(PROCESS_STEPS)):
            self.current_step = step
            yield  # Update UI
            await asyncio.sleep(1.5)  # Simulate processing time
        
        # Complete processing
        self.is_processing = False
        self.is_complete = True
        self.processing_results = self.demo_results
    
    def reset_processing(self):
        """Reset the processing state."""
        self.current_step = 0
        self.is_processing = False
        self.is_complete = False
        self.processing_results = {}
        self.error_message = ""
        self.url_input = ""


def step_indicator(step_data: Dict[str, Any], current_step: int, step_index: int) -> rx.Component:
    """Create a visual indicator for each processing step."""
    is_current = step_index == current_step
    is_completed = step_index < current_step or ProcessingState.is_complete
    
    return rx.hstack(
        rx.box(
            rx.text(
                str(step_data["id"]),
                color="white" if (is_current or is_completed) else "gray.500",
                font_weight="bold"
            ),
            bg="blue.500" if is_current else ("green.500" if is_completed else "gray.200"),
            border_radius="50%",
            width="40px",
            height="40px",
            display="flex",
            align_items="center",
            justify_content="center"
        ),
        rx.vstack(
            rx.text(
                step_data["name"],
                font_weight="bold" if is_current else "normal",
                color="blue.600" if is_current else ("green.600" if is_completed else "gray.600")
            ),
            rx.text(
                step_data["description"],
                font_size="sm",
                color="gray.500"
            ),
            align_items="start",
            spacing="1"
        ),
        align_items="center",
        spacing="4",
        p="3",
        border_radius="md",
        bg="blue.50" if is_current else ("green.50" if is_completed else "gray.50"),
        width="100%"
    )


def processing_progress() -> rx.Component:
    """Display the current processing progress."""
    return rx.vstack(
        rx.heading("Processing Status", size="6", mb="4"),
        rx.foreach(
            PROCESS_STEPS,
            lambda step, index: step_indicator(step, ProcessingState.current_step, index)
        ),
        rx.progress(
            value=rx.cond(
                ProcessingState.is_complete,
                100,
                (ProcessingState.current_step + 1) * (100 / len(PROCESS_STEPS))
            ),
            size="lg",
            color_scheme="blue",
            mt="4"
        ),
        spacing="2",
        width="100%"
    )


def results_display() -> rx.Component:
    """Display the processing results."""
    return rx.cond(
        ProcessingState.is_complete,
        rx.vstack(
            rx.heading("✅ Processing Complete!", size="6", color="green.600", mb="4"),
            
            # Basic information card
            rx.card(
                rx.vstack(
                    rx.heading("📊 Resource Analysis", size="5", mb="3"),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Topic:", font_weight="bold", color="gray.600"),
                            rx.text(ProcessingState.demo_results["parsed_data"]["topic"], font_size="lg")
                        ),
                        rx.vstack(
                            rx.text("Language:", font_weight="bold", color="gray.600"),
                            rx.text(ProcessingState.demo_results["parsed_data"]["language"], font_size="lg")
                        ),
                        rx.vstack(
                            rx.text("Total Resources:", font_weight="bold", color="gray.600"),
                            rx.text(str(ProcessingState.demo_results["parsed_data"]["total_items"]), font_size="lg")
                        ),
                        justify="space-between",
                        width="100%"
                    ),
                    rx.text(
                        ProcessingState.demo_results["parsed_data"]["description"],
                        color="gray.700",
                        mt="2"
                    ),
                    align_items="start",
                    spacing="3"
                ),
                p="6",
                bg="gray.50",
                border_radius="lg"
            ),
            
            # Categories card
            rx.card(
                rx.vstack(
                    rx.heading("📂 Learning Categories", size="5", mb="3"),
                    rx.wrap(
                        *[rx.badge(category, color_scheme="blue", mr="2", mb="2") 
                          for category in ProcessingState.demo_results["parsed_data"]["categories"][:6]],
                        spacing="2"
                    ),
                    rx.cond(
                        len(ProcessingState.demo_results["parsed_data"]["categories"]) > 6,
                        rx.text(f"... and {len(ProcessingState.demo_results['parsed_data']['categories']) - 6} more categories", 
                               color="gray.500", font_size="sm")
                    ),
                    align_items="start",
                    spacing="3"
                ),
                p="6",
                bg="blue.50",
                border_radius="lg"
            ),
            
            # Learning paths card
            rx.card(
                rx.vstack(
                    rx.heading("🛤️ Recommended Learning Paths", size="5", mb="3"),
                    rx.foreach(
                        ProcessingState.demo_results["learning_guidance"]["learning_paths"],
                        lambda path: rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.heading(path["name"], size="4"),
                                    rx.badge(path["difficulty"], color_scheme="green"),
                                    justify="space-between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text(f"⏱️ {path['estimated_hours']} hours", color="gray.600"),
                                    rx.text(f"📚 {path['resources_count']} resources", color="gray.600"),
                                    spacing="4"
                                ),
                                rx.text(f"Prerequisites: {', '.join(path['prerequisites'])}", 
                                       color="gray.500", font_size="sm"),
                                align_items="start",
                                spacing="2"
                            ),
                            p="4",
                            border="1px solid",
                            border_color="gray.200",
                            border_radius="md",
                            mb="3"
                        )
                    ),
                    align_items="start",
                    spacing="3"
                ),
                p="6",
                bg="green.50",
                border_radius="lg"
            ),
            
            # Action buttons
            rx.hstack(
                rx.button(
                    "Process Another URL",
                    on_click=ProcessingState.reset_processing,
                    color_scheme="blue",
                    size="lg"
                ),
                rx.button(
                    "Download Results",
                    color_scheme="green",
                    size="lg",
                    disabled=True  # Placeholder for future functionality
                ),
                spacing="4",
                justify="center",
                mt="6"
            ),
            
            spacing="6",
            width="100%"
        )
    )


def input_form() -> rx.Component:
    """Input form for URL submission."""
    return rx.vstack(
        rx.heading("CodeTV AI Learning Path Generator", size="9", text_align="center"),
        rx.text(
            "Transform Awesome Lists into personalized learning paths with AI-powered analysis",
            size="5",
            text_align="center",
            color="gray.600",
            mb="6"
        ),
        
        rx.card(
            rx.vstack(
                rx.heading("Enter Awesome List URL", size="6", mb="4"),
                rx.input(
                    placeholder="https://github.com/sindresorhus/awesome",
                    value=ProcessingState.url_input,
                    on_change=ProcessingState.set_url_input,
                    size="lg",
                    width="100%"
                ),
                rx.button(
                    "Generate Learning Path",
                    on_click=ProcessingState.start_processing,
                    disabled=ProcessingState.is_processing,
                    size="lg",
                    color_scheme="blue",
                    width="100%",
                    loading=ProcessingState.is_processing
                ),
                rx.cond(
                    ProcessingState.error_message != "",
                    rx.text(
                        ProcessingState.error_message,
                        color="red.500",
                        font_size="sm"
                    )
                ),
                spacing="4",
                align_items="stretch"
            ),
            p="8",
            width="100%",
            max_width="600px"
        ),
        
        # Example URLs
        rx.card(
            rx.vstack(
                rx.heading("Try these examples:", size="4", mb="3"),
                rx.vstack(
                    rx.link(
                        "🐍 Awesome Python",
                        href="javascript:void(0)",
                        on_click=lambda: ProcessingState.set_url_input("https://github.com/vinta/awesome-python"),
                        color="blue.600"
                    ),
                    rx.link(
                        "🌐 Awesome JavaScript",
                        href="javascript:void(0)",
                        on_click=lambda: ProcessingState.set_url_input("https://github.com/sorrycc/awesome-javascript"),
                        color="blue.600"
                    ),
                    rx.link(
                        "🚀 Awesome React",
                        href="javascript:void(0)",
                        on_click=lambda: ProcessingState.set_url_input("https://github.com/enaqx/awesome-react"),
                        color="blue.600"
                    ),
                    spacing="2",
                    align_items="start"
                ),
                spacing="3",
                align_items="start"
            ),
            p="6",
            bg="gray.50",
            width="100%",
            max_width="600px"
        ),
        
        spacing="6",
        align_items="center",
        width="100%"
    )


def page() -> rx.Component:
    """Main page component."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        
        rx.cond(
            ProcessingState.is_processing | ProcessingState.is_complete,
            # Processing/Results view
            rx.vstack(
                processing_progress(),
                results_display(),
                spacing="8",
                width="100%",
                min_height="85vh",
                justify="start",
                pt="8"
            ),
            # Input form view
            rx.vstack(
                input_form(),
                spacing="8",
                width="100%",
                min_height="85vh",
                justify="center"
            )
        ),
        
        # Footer
        rx.box(
            rx.text(
                "⚠️ This is a demo frontend. Processing results are simulated.",
                color="gray.500",
                font_size="sm",
                text_align="center"
            ),
            position="fixed",
            bottom="4",
            left="50%",
            transform="translateX(-50%)",
            bg="white",
            p="2",
            border_radius="md",
            shadow="sm"
        ),
        
        max_width="1200px",
        p="4"
    )
