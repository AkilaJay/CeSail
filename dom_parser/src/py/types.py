from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from pydantic import validator

class ActionType(str, Enum):
    CLICK = "click"
    HOVER = "hover"
    TYPE = "type"
    SELECT = "select"
    CHECK = "check"
    SLIDE = "slide"
    DATE_PICK = "date_pick"
    PLAY = "play"
    PAUSE = "pause"
    BACK = "back"
    FORWARD = "forward"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"
    SCROLL_TO = "scroll_to"
    SCROLL_BY = "scroll_by"
    SCROLL_DOWN_VIEWPORT = "scroll_down_viewport"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"
    DRAG_DROP = "drag_drop"
    FOCUS = "focus"
    BLUR = "blur"
    PRESS_KEY = "press_key"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    CLEAR = "clear"
    UPLOAD_FILE = "upload_file"
    SUBMIT = "submit"
    ALERT_ACCEPT = "alert_accept"
    ALERT_DISMISS = "alert_dismiss"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    WAIT = "wait"
    SWITCH_TO_FRAME = "switch_to_frame"
    SWITCH_TO_PARENT_FRAME = "switch_to_parent_frame"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"
    CUSTOM_CLICK = "custom_click"
    NAVIGATE = "navigate"

class DOMDiff(BaseModel):
    """Represents changes in the DOM structure."""
    added_elements: List[str] = []
    removed_elements: List[str] = []
    modified_elements: List[str] = []
    changes: Dict[str, Any] = {}

class SideEffect(BaseModel):
    """Represents side effects of an action."""
    type: str  # e.g., "cartUpdate", "formValidation", "modalAppearance", "ariaLiveUpdate"
    element_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class ElementInfo(BaseModel):
    """Information about a DOM element."""
    id: str
    type: str
    tag: str
    text: Optional[str] = None
    attributes: Dict[str, str] = {}
    bounding_box: Dict[str, float] = {'top': 0, 'left': 0, 'width': 0, 'height': 0}
    is_visible: bool = True
    is_interactive: bool = False
    is_sensitive: bool = False
    children: List['ElementInfo'] = []
    aria_role: Optional[str] = None
    input_type: Optional[str] = None

class Action(BaseModel):
    """Represents an action that can be performed on a page."""
    type: ActionType
    description: str = "Action"
    confidence: float = 1.0
    element_id: Optional[str] = None
    dom_diff: Optional[DOMDiff] = None
    side_effects: Optional[List[SideEffect]] = None
    text_to_type: Optional[str] = None
    options: Optional[str] = None
    value: Optional[Any] = None
    date: Optional[str] = None
    script: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('element_id')
    def validate_element_id(cls, v, values):
        if 'type' in values and values['type'] not in [ActionType.BACK, ActionType.FORWARD, ActionType.SWITCH_TAB, ActionType.CLOSE_TAB, ActionType.NAVIGATE] and not v:
            raise ValueError('element_id is required for all actions except BACK, FORWARD, SWITCH_TAB, CLOSE_TAB, and NAVIGATE')
        return v

    def to_json(self) -> Dict[str, Any]:
        """Convert the Action to a JSON-compatible dictionary."""
        return {
            "type": self.type.value,  # Convert enum to string
            "description": self.description,
            "confidence": self.confidence,
            "element_id": self.element_id,
            "dom_diff": self.dom_diff.dict() if self.dom_diff else None,
            "side_effects": [effect.dict() for effect in self.side_effects] if self.side_effects else None,
            "text_to_type": self.text_to_type,
            "options": self.options,
            "value": self.value,
            "date": self.date,
            "script": self.script,
            "metadata": self.metadata
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Action':
        """Create an Action from a JSON-compatible dictionary."""
        # Convert string type to ActionType enum
        if isinstance(data.get('type'), str):
            data['type'] = ActionType(data['type'])
        
        # Convert dom_diff dict to DOMDiff object if present
        if data.get('dom_diff'):
            data['dom_diff'] = DOMDiff(**data['dom_diff'])
        
        # Convert side_effects list to SideEffect objects if present
        if data.get('side_effects'):
            data['side_effects'] = [SideEffect(**effect) for effect in data['side_effects']]
        
        return cls(**data)

    @classmethod
    def from_action_schema(cls, action_type: str, params: Dict[str, Any]) -> 'Action':
        """
        Create an Action from the action schema format.
        
        Args:
            action_type: The type of action (e.g., 'click', 'type', etc.)
            params: Dictionary containing the action parameters
            
        Returns:
            Action object configured according to the schema
        """
        # Get the action schema
        schema = get_available_actions()['actions'].get(action_type)
        if not schema:
            raise ValueError(f"Unknown action type: {action_type}")
        
        # Validate required parameters
        for required_param in schema['required_params']:
            if required_param not in params:
                raise ValueError(f"Missing required parameter: {required_param}")
        
        # Build the action data
        action_data = {
            "type": ActionType(action_type),
            "description": schema['description'],
            "confidence": 1.0,  # Default confidence
            "metadata": {}
        }
        
        # Add parameters
        for param, value in params.items():
            if param in ['element_id', 'text_to_type', 'options']:
                action_data[param] = value
            else:
                action_data['metadata'][param] = value
        
        return cls(**action_data)

class ParsedAction(BaseModel):
    """Represents an action parsed from element data."""
    type: str
    bbox: Optional[Dict[str, float]] = None
    selector: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    text: Optional[str] = None
    importantText: Optional[str] = None
    score: Optional[float] = None
    tag: Optional[str] = None
    rect: Optional[Dict[str, float]] = None
    interactive: Optional[bool] = None
    sensitive: Optional[bool] = None
    role: Optional[str] = None
    aria: Optional[Dict[str, Optional[str]]] = None
    computedStyle: Optional[Dict[str, str]] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParsedAction':
        """Create a ParsedAction from element data JSON."""
        return cls(
            type=data.get('type', ''),
            bbox=data.get('bbox'),
            selector=data.get('selector'),
            attributes=data.get('attributes'),
            text=data.get('text'),
            importantText=data.get('importantText'),
            score=data.get('score'),
            tag=data.get('tag'),
            rect=data.get('rect'),
            interactive=data.get('interactive'),
            sensitive=data.get('sensitive'),
            role=data.get('role'),
            aria=data.get('aria'),
            computedStyle=data.get('computedStyle')
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert the ParsedAction to a JSON-compatible dictionary, only including non-None fields."""
        result = {}
        
        if self.type is not None:
            result["type"] = self.type
        if self.bbox is not None:
            result["bbox"] = self.bbox
        if self.selector is not None:
            result["selector"] = self.selector
        if self.attributes is not None:
            result["attributes"] = self.attributes
        if self.text is not None:
            result["text"] = self.text
        if self.importantText is not None:
            result["importantText"] = self.importantText
        if self.score is not None:
            result["score"] = self.score
        if self.tag is not None:
            result["tag"] = self.tag
        if self.rect is not None:
            result["rect"] = self.rect
        if self.interactive is not None:
            result["interactive"] = self.interactive
        if self.sensitive is not None:
            result["sensitive"] = self.sensitive
        if self.role is not None:
            result["role"] = self.role
        if self.aria is not None:
            result["aria"] = self.aria
        if self.computedStyle is not None:
            result["computedStyle"] = self.computedStyle
            
        return result

class ParsedActionList(BaseModel):
    """A container for a list of ParsedAction objects."""
    actions: List[ParsedAction]

    @classmethod
    def from_json_list(cls, data: List[Dict[str, Any]]) -> 'ParsedActionList':
        """Create a ParsedActionList from a list of element data JSON objects."""
        return cls(actions=[ParsedAction.from_json(item) for item in data])

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the ParsedActionList to a list of JSON-compatible dictionaries."""
        return [action.to_json() for action in self.actions]

class ParsedForm(BaseModel):
    """Represents a parsed form from the DOM."""
    id: Optional[str] = None
    action: Optional[str] = None
    method: str = "get"
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    selector: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ParsedForm":
        """Create a ParsedForm from JSON data."""
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        """Convert the ParsedForm to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "action": self.action,
            "method": self.method,
            "fields": self.fields,
            "selector": self.selector
        }

class ParsedFormList(BaseModel):
    """Container for a list of ParsedForm objects."""
    forms: List[ParsedForm] = Field(default_factory=list)

    @classmethod
    def from_json_list(cls, data: List[Dict[str, Any]]) -> "ParsedFormList":
        """Create a ParsedFormList from a list of JSON dictionaries."""
        return cls(forms=[ParsedForm.from_json(form_data) for form_data in data])

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the ParsedFormList to a list of JSON-compatible dictionaries."""
        return [form.to_json() for form in self.forms]

class ParsedMetaData(BaseModel):
    """Represents parsed metadata from a webpage."""
    url: str
    canonical: Optional[str] = None
    title: str
    meta: Dict[str, Any] = Field(default_factory=lambda: {
        "description": None,
        "keywords": None,
        "viewport": None,
        "og": {
            "title": None,
            "description": None,
            "image": None
        }
    })
    status: str = "loading"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ParsedMetaData":
        """Create a ParsedMetaData from JSON data."""
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        """Convert the ParsedMetaData to a JSON-compatible dictionary."""
        return {
            "url": self.url,
            "canonical": self.canonical,
            "title": self.title,
            "meta": self.meta,
            "status": self.status
        }

class ParsedMetaDataList(BaseModel):
    """Container for a list of ParsedMetaData objects."""
    metadata: List[ParsedMetaData] = Field(default_factory=list)

    @classmethod
    def from_json_list(cls, data: List[Dict[str, Any]]) -> "ParsedMetaDataList":
        """Create a ParsedMetaDataList from a list of JSON dictionaries."""
        return cls(metadata=[ParsedMetaData.from_json(meta_data) for meta_data in data])

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the ParsedMetaDataList to a list of JSON-compatible dictionaries."""
        return [metadata.to_json() for metadata in self.metadata]

class ParsedImportantElement(BaseModel):
    """Represents an important element from the DOM."""
    tag: str
    text: Optional[str]
    type: str
    attributes: Dict[str, str]
    rect: Dict[str, float]
    selector: str
    isInteractive: bool
    hasClickHandler: bool
    isFocusable: bool
    ariaRole: Optional[str]
    computedStyle: Dict[str, str]
    importance_score: float

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ParsedImportantElement":
        """Create a ParsedImportantElement from JSON data."""
        return cls(
            tag=data.get('tag', ''),
            text=data.get('text'),
            type=data.get('type', ''),
            attributes=data.get('attributes', {}),
            rect=data.get('rect', {'x': 0, 'y': 0, 'width': 0, 'height': 0}),
            selector=data.get('selector', ''),
            isInteractive=data.get('isInteractive', False),
            hasClickHandler=data.get('hasClickHandler', False),
            isFocusable=data.get('isFocusable', False),
            ariaRole=data.get('ariaRole'),
            computedStyle=data.get('computedStyle', {
                'display': 'none',
                'position': 'static',
                'zIndex': '0',
                'cursor': 'default'
            }),
            importance_score=data.get('importance_score', 0.0)
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert the ParsedImportantElement to a JSON-compatible dictionary."""
        return {
            "tag": self.tag,
            "text": self.text,
            "type": self.type,
            "attributes": self.attributes,
            "rect": self.rect,
            "selector": self.selector,
            "isInteractive": self.isInteractive,
            "hasClickHandler": self.hasClickHandler,
            "isFocusable": self.isFocusable,
            "ariaRole": self.ariaRole,
            "computedStyle": self.computedStyle,
            "importance_score": self.importance_score
        }

class ParsedImportantElementList(BaseModel):
    """Container for a list of ParsedImportantElement objects."""
    elements: List[ParsedImportantElement] = Field(default_factory=list)

    @classmethod
    def from_json_list(cls, data: List[Dict[str, Any]]) -> "ParsedImportantElementList":
        """Create a ParsedImportantElementList from a list of JSON dictionaries."""
        return cls(elements=[ParsedImportantElement.from_json(element_data) for element_data in data])

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the ParsedImportantElementList to a list of JSON-compatible dictionaries."""
        return [element.to_json() for element in self.elements]

class ParsedPage(BaseModel):
    """A container class that holds all parsed data from a webpage."""
    actions: ParsedActionList = Field(default_factory=lambda: ParsedActionList(actions=[]))
    forms: ParsedFormList = Field(default_factory=lambda: ParsedFormList(forms=[]))
    metadata: ParsedMetaData = Field(default_factory=lambda: ParsedMetaData(url="", title=""))
    important_elements: ParsedImportantElementList = Field(default_factory=lambda: ParsedImportantElementList(elements=[]))

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ParsedPage":
        """Create a ParsedPage from JSON data."""
        return cls(
            actions=ParsedActionList.from_json_list(data.get("actions", [])),
            forms=ParsedFormList.from_json_list(data.get("forms", [])),
            metadata=ParsedMetaData.from_json(data.get("metadata", {"url": "", "title": ""})),
            important_elements=ParsedImportantElementList.from_json_list(data.get("important_elements", []))
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert the ParsedPage to a JSON-compatible dictionary."""
        return {
            "actions": self.actions.to_json(),
            "forms": self.forms.to_json(),
            "metadata": self.metadata.to_json(),
            "important_elements": self.important_elements.to_json()
        }

    def get_actions(self) -> List[ParsedAction]:
        """Get all actions from the page."""
        return self.actions.actions

    def get_forms(self) -> List[ParsedForm]:
        """Get all forms from the page."""
        return self.forms.forms

    def get_metadata(self) -> ParsedMetaData:
        """Get the page metadata."""
        return self.metadata

    def get_important_elements(self) -> List[ParsedImportantElement]:
        """Get all important elements from the page."""
        return self.important_elements.elements

class ActionResult(BaseModel):
    """Represents the result of executing an action."""
    success: bool
    error: Optional[str] = None
    side_effects: Optional[List[SideEffect]] = None
    data: Optional[Dict[str, Any]] = None

# Type alias for ElementInfo
Element = ElementInfo
