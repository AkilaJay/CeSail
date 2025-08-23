import json
from typing import Dict, Any, Optional
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "browser": {
        "headless": False,
        "browser_type": "chromium",
        "browser_args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--enable-logging",
            "--v=1"
        ],
        "context_options": {},
        "extra_http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"'
        }
    },
    "action_executor": {
        "enabled_actions": [
            "click", "type", "hover", "select", "check", "clear", "submit",
            "navigate", "back", "forward", "scroll_to", "scroll_by", "scroll_down_viewport",
            "right_click", "double_click", "focus", "blur", "drag_drop",
            "press_key", "key_down", "key_up", "upload_file",
            "alert_accept", "alert_dismiss", "wait", "wait_for_selector", "wait_for_navigation",
            "switch_to_frame", "switch_to_parent_frame", "switch_tab", "close_tab"
        ],
    },
    "idle_watcher": {
        "default_idle_time_ms": 300,
        "mutation_timeout_ms": 5000,
        "network_idle_timeout_ms": 1000,
        "enable_console_logging": True,
        "log_idle_events": False,
        "strict_idle_detection": False
    },
    "page_analyzer": {
        "element_extraction": {
            "extract_forms": True,
            "extract_media": True,
            "extract_links": True,
            "extract_structured_data": True,
            "extract_dynamic_state": True,
            "extract_layout_info": True,
            "extract_pagination_info": True,
            "extract_meta_data": True,
            "extract_document_outline": True,
            "extract_text_content": True,
            "actions": {
                "enable_mapping": True,
                "show_bounding_boxes": True,
                "action_filters": {
                    "include_fields": [
                        "type", "selector", "importantText"
                    ],
                    "exclude_fields": [],
                    "important_text_max_length": 250,
                    "trim_text_to_length": 100
                }
            },
        },
    },
    "screenshot": {
        "default_format": "png",
        "default_quality": 90
    },
    "global": {
        "bundle_path": None,
        "enable_console_logging": True,
        "log_level": "INFO"
    }
}

def load_config(filepath: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load configuration from file or dict, merging with defaults.
    
    Args:
        filepath: Path to JSON config file
        config_dict: Configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    if filepath:
        with open(filepath, 'r') as f:
            file_config = json.load(f)
        _deep_merge(config, file_config)
    
    if config_dict:
        _deep_merge(config, config_dict)
    
    return config

def save_config(config: Dict[str, Any], filepath: str) -> None:
    """Save configuration to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)

def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> None:
    """Recursively merge update dict into base dict."""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value

def get_module_config(config: Dict[str, Any], module_name: str) -> Dict[str, Any]:
    """Get configuration for a specific module."""
    return config.get(module_name, {})

def validate_config(config: Dict[str, Any]) -> bool:
    """Basic validation of configuration."""
    required_sections = ["browser", "action_executor", "idle_watcher", "page_analyzer", "screenshot"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate browser config
    browser = config["browser"]
    if "headless" not in browser:
        raise ValueError("browser.headless is required")
    if "browser_type" not in browser:
        raise ValueError("browser.browser_type is required")
    
    idle_watcher = config["idle_watcher"]
    if idle_watcher.get("default_idle_time_ms", 0) <= 0:
        raise ValueError("idle_watcher.default_idle_time_ms must be positive")
    
    return True

# Example configurations
EXAMPLE_CONFIGS = {
    "development": {
        "browser": {"headless": False},
        "action_executor": {"log_action_execution": True},
        "idle_watcher": {"default_idle_time_ms": 500},
        "page_analyzer": {"enable_visual_debugging": True},
        "global": {"log_level": "DEBUG"}
    },
    "production": {
        "browser": {"headless": True},
        "action_executor": {"retry_failed_actions": True, "max_retries": 5},
        "idle_watcher": {"default_idle_time_ms": 200},
        "page_analyzer": {"max_elements_to_extract": 500},
        "global": {"log_level": "WARNING"}
    },
    "testing": {
        "browser": {"headless": True},
        "action_executor": {"default_timeout_ms": 10000},
        "idle_watcher": {"default_idle_time_ms": 100},
        "page_analyzer": {"max_elements_to_extract": 100},
        "global": {"log_level": "ERROR"}
    }
} 