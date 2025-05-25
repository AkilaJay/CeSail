from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class ElementType(str, Enum):
    BUTTON = "BUTTON"
    LINK = "LINK"
    INPUT = "INPUT"
    TEXTAREA = "TEXTAREA"
    SELECT = "SELECT"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    TOGGLE = "TOGGLE"
    SLIDER = "SLIDER"
    DATEPICKER = "DATEPICKER"
    FILE_INPUT = "FILE_INPUT"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    TABLE = "TABLE"
    TABLE_ROW = "TABLE_ROW"
    TABLE_CELL = "TABLE_CELL"
    FORM = "FORM"
    SVG = "SVG"
    CANVAS = "CANVAS"
    IFRAME = "IFRAME"
    OTHER = "OTHER"
    TAB = "TAB"

class ActionType(str, Enum):
    CLICK = "click"
    HOVER = "hover"
    TYPE = "type"
    SELECT = "select"
    CHECK = "check"
    TOGGLE = "toggle"
    SLIDE = "slide"
    DATE_PICK = "date_pick"
    PLAY = "play"
    PAUSE = "pause"
    BACK = "back"
    FORWARD = "forward"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"

class BoundingBox(BaseModel):
    top: float
    left: float
    width: float
    height: float

class MetaData(BaseModel):
    url: str
    canonical: Optional[str]
    title: str
    meta: Dict[str, Any]
    status: str

class DocumentOutline(BaseModel):
    level: int
    text: str
    id: Optional[str]

class TextBlock(BaseModel):
    type: str
    text: str
    id: Optional[str]

class FormField(BaseModel):
    type: str
    name: Optional[str]
    id: Optional[str]
    placeholder: Optional[str]
    value: Optional[str]
    required: bool
    pattern: Optional[str]
    min: Optional[str]
    max: Optional[str]
    options: Optional[List[Dict[str, str]]]

class Form(BaseModel):
    id: Optional[str]
    action: Optional[str]
    method: Optional[str]
    fields: List[FormField]

class MediaElement(BaseModel):
    type: str
    src: str
    alt: Optional[str]
    width: Optional[int]
    height: Optional[int]
    loading: Optional[str]
    controls: Optional[bool]
    autoplay: Optional[bool]
    loop: Optional[bool]
    muted: Optional[bool]

class Link(BaseModel):
    href: str
    text: str
    target: Optional[str]
    rel: Optional[str]

class DynamicElement(BaseModel):
    id: Optional[str]
    role: Optional[str]
    text: str
    type: Optional[str]

class DynamicState(BaseModel):
    modals: List[DynamicElement]
    notifications: List[DynamicElement]
    loading: List[DynamicElement]

class LayoutInfo(BaseModel):
    type: str
    id: Optional[str]
    rect: Dict[str, float]
    zIndex: str

class PaginationInfo(BaseModel):
    next: Optional[str]
    prev: Optional[str]
    pages: List[Dict[str, Any]]

class ElementInfo(BaseModel):
    id: str
    type: ElementType
    tag: str
    text: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    bounding_box: BoundingBox
    is_visible: bool = True
    is_interactive: bool = False
    is_sensitive: bool = False
    children: List['ElementInfo'] = Field(default_factory=list)
    aria_role: Optional[str] = None
    input_type: Optional[str] = None

class Action(BaseModel):
    type: ActionType
    description: str
    confidence: float
    element_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PageAnalysis(BaseModel):
    meta: MetaData
    outline: List[DocumentOutline]
    text: List[TextBlock]
    forms: List[Form]
    media: List[MediaElement]
    links: List[Link]
    structuredData: List[Dict[str, Any]]
    dynamic: DynamicState
    actions: List[Action]
    layout: List[LayoutInfo]
    pagination: PaginationInfo
    elements: List[ElementInfo]

class ActionGraph(BaseModel):
    url: str
    nodes: List[ElementInfo]
    edges: List[Action]
    metadata: Dict[str, Any] = Field(default_factory=dict)
