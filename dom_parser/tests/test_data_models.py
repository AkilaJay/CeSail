import pytest
from dom_parser.src.py.types import (
    ParsedAction, ParsedActionList, ParsedForm, ParsedFormList,
    ParsedMetaData, ParsedMetaDataList, ParsedImportantElement, ParsedImportantElementList,
    ParsedPage
)

class TestParser:
    """Test cases for ParsedAction parser functionality."""

    def test_basic_element_parsing(self):
        """Test basic element parsing functionality."""
        # Test link element
        link_data = {
            "tag": "a",
            "attributes": {
                "href": "https://example.com",
                "class": "nav-link"
            },
            "text": "Click me",
            "rect": {"x": 100, "y": 200, "width": 150, "height": 40},
            "interactive": True,
            "type": "link",
            "sensitive": False,
            "role": None,
            "aria": {
                "label": None,
                "describedby": None,
                "labelledby": None
            },
            "computedStyle": {
                "display": "inline-block",
                "visibility": "visible",
                "zIndex": "1"
            },
            "selector": "a.nav-link"
        }
        
        parsed_action = ParsedAction.from_json(link_data)
        assert parsed_action.tag == "a"
        assert parsed_action.attributes == link_data["attributes"]
        assert parsed_action.text == "Click me"
        assert parsed_action.interactive is True
        assert parsed_action.type == "link"
        assert parsed_action.selector == "a.nav-link"

        # Test to_json
        json_data = parsed_action.to_json()
        assert json_data["tag"] == "a"
        assert json_data["attributes"] == link_data["attributes"]
        assert json_data["text"] == "Click me"
        assert json_data["interactive"] is True
        assert json_data["type"] == "link"
        assert json_data["selector"] == "a.nav-link"

    def test_form_elements(self):
        """Test parsing of various form elements."""
        # Test required email input
        email_data = {
            "tag": "input",
            "attributes": {
                "type": "email",
                "placeholder": "Enter email",
                "required": "true"
            },
            "text": "",
            "rect": {"x": 100, "y": 200, "width": 300, "height": 40},
            "interactive": True,
            "type": "email",
            "sensitive": False,
            "role": None,
            "aria": {
                "label": None,
                "describedby": None,
                "labelledby": None
            },
            "computedStyle": {
                "display": "block",
                "visibility": "visible",
                "zIndex": "1"
            },
            "selector": "input[type='email']"
        }
        
        parsed_action = ParsedAction.from_json(email_data)
        assert parsed_action.tag == "input"
        assert parsed_action.attributes == email_data["attributes"]
        assert parsed_action.type == "email"
        assert parsed_action.interactive is True
        assert parsed_action.selector == "input[type='email']"

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test empty attributes
        empty_attrs_data = {
            "tag": "div",
            "attributes": {},
            "text": "",
            "rect": {"x": 0, "y": 0, "width": 0, "height": 0},
            "interactive": False,
            "type": "div",
            "sensitive": False,
            "role": None,
            "aria": {},
            "computedStyle": {},
            "selector": ""
        }
        
        parsed_action = ParsedAction.from_json(empty_attrs_data)
        assert parsed_action.tag == "div"
        assert parsed_action.attributes == {}
        assert parsed_action.text == ""
        assert parsed_action.interactive is False
        assert parsed_action.selector == ""

        # Test missing fields (Pydantic will use default values)
        minimal_data = {
            "tag": "div",
            "interactive": True
        }
        
        parsed_action = ParsedAction.from_json(minimal_data)
        assert parsed_action.tag == "div"
        assert parsed_action.attributes is None
        assert parsed_action.text is None
        assert parsed_action.interactive is True
        assert parsed_action.type == ""
        assert parsed_action.sensitive is None
        assert parsed_action.role is None
        assert parsed_action.aria is None
        assert parsed_action.computedStyle is None
        assert parsed_action.selector is None

    def test_special_elements(self):
        """Test parsing of special elements like images and summaries."""
        # Test clickable image
        image_data = {
            "tag": "img",
            "attributes": {
                "src": "button.png",
                "alt": "Click me",
                "role": "button"
            },
            "text": "",
            "rect": {"x": 100, "y": 200, "width": 100, "height": 100},
            "interactive": True,
            "type": "img",
            "sensitive": False,
            "role": "button",
            "aria": {},
            "computedStyle": {},
            "selector": "img[role='button']"
        }
        
        parsed_action = ParsedAction.from_json(image_data)
        assert parsed_action.tag == "img"
        assert parsed_action.attributes == image_data["attributes"]
        assert parsed_action.role == "button"
        assert parsed_action.interactive is True
        assert parsed_action.selector == "img[role='button']"

    def test_aria_roles(self):
        """Test parsing of elements with ARIA roles."""
        # Test button role
        button_role_data = {
            "tag": "div",
            "attributes": {
                "role": "button",
                "aria-label": "Submit form"
            },
            "text": "",
            "rect": {"x": 100, "y": 200, "width": 150, "height": 40},
            "interactive": True,
            "type": "div",
            "sensitive": False,
            "role": "button",
            "aria": {
                "label": "Submit form",
                "describedby": None,
                "labelledby": None
            },
            "computedStyle": {},
            "selector": "div[role='button']"
        }
        
        parsed_action = ParsedAction.from_json(button_role_data)
        assert parsed_action.tag == "div"
        assert parsed_action.attributes == button_role_data["attributes"]
        assert parsed_action.role == "button"
        assert parsed_action.aria["label"] == "Submit form"
        assert parsed_action.interactive is True
        assert parsed_action.selector == "div[role='button']"

    def test_sensitive_elements(self):
        """Test parsing of sensitive elements."""
        # Test password input
        password_data = {
            "tag": "input",
            "attributes": {
                "type": "password",
                "placeholder": "Enter password"
            },
            "text": "",
            "rect": {"x": 100, "y": 200, "width": 300, "height": 40},
            "interactive": True,
            "type": "password",
            "sensitive": True,
            "role": None,
            "aria": {},
            "computedStyle": {},
            "selector": "input[type='password']"
        }
        
        parsed_action = ParsedAction.from_json(password_data)
        assert parsed_action.tag == "input"
        assert parsed_action.attributes == password_data["attributes"]
        assert parsed_action.type == "password"
        assert parsed_action.sensitive is True
        assert parsed_action.interactive is True
        assert parsed_action.selector == "input[type='password']"

    def test_parsed_action_list_from_json(self):
        """Test creating ParsedActionList from a list of JSON dicts."""
        json_list = [
            {
                "tag": "a",
                "attributes": {"href": "#"},
                "text": "Link",
                "rect": {"x": 1, "y": 2, "width": 3, "height": 4},
                "interactive": True,
                "type": "link",
                "sensitive": False,
                "role": None,
                "aria": {},
                "computedStyle": {},
                "selector": "a"
            },
            {
                "tag": "input",
                "attributes": {"type": "text"},
                "text": "",
                "rect": {"x": 5, "y": 6, "width": 7, "height": 8},
                "interactive": True,
                "type": "text",
                "sensitive": False,
                "role": None,
                "aria": {},
                "computedStyle": {},
                "selector": "input"
            }
        ]
        palist = ParsedActionList.from_json_list(json_list)
        assert isinstance(palist, ParsedActionList)
        assert len(palist.actions) == 2
        assert all(isinstance(a, ParsedAction) for a in palist.actions)
        assert palist.actions[0].tag == "a"
        assert palist.actions[1].tag == "input"

        # Test to_json
        json_data = palist.to_json()
        assert len(json_data) == 2
        assert json_data[0]["tag"] == "a"
        assert json_data[1]["tag"] == "input"

    def test_parsed_action_list_empty(self):
        """Test creating ParsedActionList from an empty list."""
        palist = ParsedActionList.from_json_list([])
        assert isinstance(palist, ParsedActionList)
        assert palist.actions == []

    def test_parsed_form_from_json(self):
        """Test creating ParsedForm from JSON data."""
        form_data = {
            "id": "login-form",
            "action": "/login",
            "method": "post",
            "selector": "form#login-form",
            "fields": [
                {
                    "type": "email",
                    "name": "email",
                    "id": "email-input",
                    "placeholder": "Enter email",
                    "required": True
                },
                {
                    "type": "password",
                    "name": "password",
                    "id": "password-input",
                    "placeholder": "Enter password",
                    "required": True
                }
            ]
        }
        
        parsed_form = ParsedForm.from_json(form_data)
        assert parsed_form.id == "login-form"
        assert parsed_form.action == "/login"
        assert parsed_form.method == "post"
        assert parsed_form.selector == "form#login-form"
        assert len(parsed_form.fields) == 2
        assert parsed_form.fields[0]["type"] == "email"
        assert parsed_form.fields[1]["type"] == "password"

        # Test to_json
        json_data = parsed_form.to_json()
        assert json_data["id"] == "login-form"
        assert json_data["action"] == "/login"
        assert json_data["method"] == "post"
        assert json_data["selector"] == "form#login-form"
        assert len(json_data["fields"]) == 2
        assert json_data["fields"][0]["type"] == "email"
        assert json_data["fields"][1]["type"] == "password"

    def test_parsed_form_minimal(self):
        """Test creating ParsedForm with minimal data."""
        minimal_data = {
            "id": "simple-form",
            "fields": []
        }
        
        parsed_form = ParsedForm.from_json(minimal_data)
        assert parsed_form.id == "simple-form"
        assert parsed_form.action is None
        assert parsed_form.method == "get"  # default value
        assert parsed_form.fields == []

    def test_parsed_form_list_from_json(self):
        """Test creating ParsedFormList from a list of JSON dicts."""
        json_list = [
            {
                "id": "form1",
                "action": "/submit1",
                "method": "post",
                "fields": [
                    {
                        "type": "text",
                        "name": "field1",
                        "required": True
                    }
                ]
            },
            {
                "id": "form2",
                "action": "/submit2",
                "method": "get",
                "fields": [
                    {
                        "type": "select",
                        "name": "field2",
                        "options": [
                            {"value": "1", "text": "Option 1"},
                            {"value": "2", "text": "Option 2"}
                        ]
                    }
                ]
            }
        ]
        
        form_list = ParsedFormList.from_json_list(json_list)
        assert isinstance(form_list, ParsedFormList)
        assert len(form_list.forms) == 2
        assert all(isinstance(f, ParsedForm) for f in form_list.forms)
        assert form_list.forms[0].id == "form1"
        assert form_list.forms[1].id == "form2"
        assert len(form_list.forms[0].fields) == 1
        assert len(form_list.forms[1].fields) == 1

        # Test to_json
        json_data = form_list.to_json()
        assert len(json_data) == 2
        assert json_data[0]["id"] == "form1"
        assert json_data[1]["id"] == "form2"
        assert len(json_data[0]["fields"]) == 1
        assert len(json_data[1]["fields"]) == 1

    def test_parsed_form_list_empty(self):
        """Test creating ParsedFormList from an empty list."""
        form_list = ParsedFormList.from_json_list([])
        assert isinstance(form_list, ParsedFormList)
        assert form_list.forms == []

    def test_parsed_metadata_from_json(self):
        """Test creating ParsedMetaData from JSON data."""
        metadata = {
            "url": "https://example.com",
            "canonical": "https://example.com/canonical",
            "title": "Example Page",
            "meta": {
                "description": "This is an example page",
                "keywords": "example, test, page",
                "viewport": "width=device-width, initial-scale=1",
                "og": {
                    "title": "Example Page - Open Graph",
                    "description": "OG description",
                    "image": "https://example.com/image.jpg"
                }
            },
            "status": "complete"
        }
        
        parsed_metadata = ParsedMetaData.from_json(metadata)
        assert parsed_metadata.url == "https://example.com"
        assert parsed_metadata.canonical == "https://example.com/canonical"
        assert parsed_metadata.title == "Example Page"
        assert parsed_metadata.meta["description"] == "This is an example page"
        assert parsed_metadata.meta["keywords"] == "example, test, page"
        assert parsed_metadata.meta["og"]["title"] == "Example Page - Open Graph"
        assert parsed_metadata.status == "complete"

        # Test to_json
        json_data = parsed_metadata.to_json()
        assert json_data["url"] == "https://example.com"
        assert json_data["canonical"] == "https://example.com/canonical"
        assert json_data["title"] == "Example Page"
        assert json_data["meta"]["description"] == "This is an example page"
        assert json_data["meta"]["keywords"] == "example, test, page"
        assert json_data["meta"]["og"]["title"] == "Example Page - Open Graph"
        assert json_data["status"] == "complete"

    def test_parsed_metadata_minimal(self):
        """Test creating ParsedMetaData with minimal data."""
        minimal_data = {
            "url": "https://example.com",
            "title": "Example Page"
        }
        
        parsed_metadata = ParsedMetaData.from_json(minimal_data)
        assert parsed_metadata.url == "https://example.com"
        assert parsed_metadata.title == "Example Page"
        assert parsed_metadata.canonical is None
        assert parsed_metadata.meta["description"] is None
        assert parsed_metadata.meta["og"]["title"] is None
        assert parsed_metadata.status == "loading"  # default value

    def test_parsed_metadata_list_from_json(self):
        """Test creating ParsedMetaDataList from a list of JSON dicts."""
        json_list = [
            {
                "url": "https://example.com/page1",
                "title": "Page 1",
                "status": "complete"
            },
            {
                "url": "https://example.com/page2",
                "title": "Page 2",
                "meta": {
                    "description": "Page 2 description",
                    "og": {
                        "title": "Page 2 OG Title"
                    }
                },
                "status": "loading"
            }
        ]
        
        metadata_list = ParsedMetaDataList.from_json_list(json_list)
        assert isinstance(metadata_list, ParsedMetaDataList)
        assert len(metadata_list.metadata) == 2
        assert all(isinstance(m, ParsedMetaData) for m in metadata_list.metadata)
        assert metadata_list.metadata[0].url == "https://example.com/page1"
        assert metadata_list.metadata[1].url == "https://example.com/page2"
        assert metadata_list.metadata[0].status == "complete"
        assert metadata_list.metadata[1].status == "loading"

        # Test to_json
        json_data = metadata_list.to_json()
        assert len(json_data) == 2
        assert json_data[0]["url"] == "https://example.com/page1"
        assert json_data[1]["url"] == "https://example.com/page2"
        assert json_data[0]["status"] == "complete"
        assert json_data[1]["status"] == "loading"

    def test_parsed_metadata_list_empty(self):
        """Test creating ParsedMetaDataList from an empty list."""
        metadata_list = ParsedMetaDataList.from_json_list([])
        assert isinstance(metadata_list, ParsedMetaDataList)
        assert metadata_list.metadata == []

    def test_parsed_important_element_from_json(self):
        """Test creating ParsedImportantElement from JSON data."""
        element_data = {
            "tag": "button",
            "text": "Click me",
            "type": "button",
            "attributes": {
                "class": "primary-button",
                "aria-label": "Submit form"
            },
            "rect": {
                "x": 100,
                "y": 200,
                "width": 150,
                "height": 40
            },
            "selector": "button.primary-button",
            "isInteractive": True,
            "hasClickHandler": True,
            "isFocusable": True,
            "ariaRole": "button",
            "computedStyle": {
                "display": "block",
                "position": "relative",
                "zIndex": "1",
                "cursor": "pointer"
            },
            "importance_score": 0.85
        }
        
        parsed_element = ParsedImportantElement.from_json(element_data)
        assert parsed_element.tag == "button"
        assert parsed_element.text == "Click me"
        assert parsed_element.type == "button"
        assert parsed_element.attributes["class"] == "primary-button"
        assert parsed_element.rect["x"] == 100
        assert parsed_element.selector == "button.primary-button"
        assert parsed_element.isInteractive is True
        assert parsed_element.hasClickHandler is True
        assert parsed_element.isFocusable is True
        assert parsed_element.ariaRole == "button"
        assert parsed_element.computedStyle["cursor"] == "pointer"
        assert parsed_element.importance_score == 0.85

        # Test to_json
        json_data = parsed_element.to_json()
        assert json_data["tag"] == "button"
        assert json_data["text"] == "Click me"
        assert json_data["type"] == "button"
        assert json_data["attributes"]["class"] == "primary-button"
        assert json_data["rect"]["x"] == 100
        assert json_data["selector"] == "button.primary-button"
        assert json_data["isInteractive"] is True
        assert json_data["hasClickHandler"] is True
        assert json_data["isFocusable"] is True
        assert json_data["ariaRole"] == "button"
        assert json_data["computedStyle"]["cursor"] == "pointer"
        assert json_data["importance_score"] == 0.85

    def test_parsed_important_element_minimal(self):
        """Test creating ParsedImportantElement with minimal data."""
        minimal_data = {
            "tag": "div",
            "type": "div",
            "selector": "div.content"
        }
        
        parsed_element = ParsedImportantElement.from_json(minimal_data)
        assert parsed_element.tag == "div"
        assert parsed_element.text is None
        assert parsed_element.type == "div"
        assert parsed_element.attributes == {}
        assert parsed_element.rect == {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        assert parsed_element.selector == "div.content"
        assert parsed_element.isInteractive is False
        assert parsed_element.hasClickHandler is False
        assert parsed_element.isFocusable is False
        assert parsed_element.ariaRole is None
        assert parsed_element.computedStyle == {
            'display': 'none',
            'position': 'static',
            'zIndex': '0',
            'cursor': 'default'
        }
        assert parsed_element.importance_score == 0.0

    def test_parsed_important_element_list_from_json(self):
        """Test creating ParsedImportantElementList from a list of JSON dicts."""
        json_list = [
            {
                "tag": "button",
                "text": "Submit",
                "type": "button",
                "selector": "button.submit",
                "importance_score": 0.9
            },
            {
                "tag": "a",
                "text": "Learn more",
                "type": "link",
                "selector": "a.learn-more",
                "importance_score": 0.7
            }
        ]
        
        element_list = ParsedImportantElementList.from_json_list(json_list)
        assert isinstance(element_list, ParsedImportantElementList)
        assert len(element_list.elements) == 2
        assert all(isinstance(e, ParsedImportantElement) for e in element_list.elements)
        assert element_list.elements[0].tag == "button"
        assert element_list.elements[1].tag == "a"
        assert element_list.elements[0].importance_score == 0.9
        assert element_list.elements[1].importance_score == 0.7

        # Test to_json
        json_data = element_list.to_json()
        assert len(json_data) == 2
        assert json_data[0]["tag"] == "button"
        assert json_data[1]["tag"] == "a"
        assert json_data[0]["importance_score"] == 0.9
        assert json_data[1]["importance_score"] == 0.7

    def test_parsed_important_element_list_empty(self):
        """Test creating ParsedImportantElementList from an empty list."""
        element_list = ParsedImportantElementList.from_json_list([])
        assert isinstance(element_list, ParsedImportantElementList)
        assert element_list.elements == []

    def test_parsed_page_from_json(self):
        """Test creating ParsedPage from JSON data."""
        page_data = {
            "actions": [
                {
                    "tag": "button",
                    "attributes": {"class": "submit"},
                    "text": "Submit",
                    "rect": {"x": 100, "y": 200, "width": 150, "height": 40},
                    "interactive": True,
                    "type": "button",
                    "sensitive": False,
                    "role": None,
                    "aria": {},
                    "computedStyle": {},
                    "selector": "button.submit"
                }
            ],
            "forms": [
                {
                    "id": "login-form",
                    "action": "/login",
                    "method": "post",
                    "fields": [
                        {
                            "type": "email",
                            "name": "email",
                            "required": True
                        }
                    ]
                }
            ],
            "metadata": {
                "url": "https://example.com",
                "title": "Example Page",
                "meta": {
                    "description": "Test page",
                    "og": {
                        "title": "OG Title"
                    }
                }
            },
            "important_elements": [
                {
                    "tag": "button",
                    "text": "Submit",
                    "type": "button",
                    "selector": "button.submit",
                    "importance_score": 0.9
                }
            ]
        }
        
        parsed_page = ParsedPage.from_json(page_data)
        assert isinstance(parsed_page, ParsedPage)
        assert len(parsed_page.actions.actions) == 1
        assert len(parsed_page.forms.forms) == 1
        assert parsed_page.metadata.url == "https://example.com"
        assert len(parsed_page.important_elements.elements) == 1
        
        # Test to_json
        json_data = parsed_page.to_json()
        assert len(json_data["actions"]) == 1
        assert len(json_data["forms"]) == 1
        assert json_data["metadata"]["url"] == "https://example.com"
        assert len(json_data["important_elements"]) == 1

    def test_parsed_page_minimal(self):
        """Test creating ParsedPage with minimal data."""
        minimal_data = {
            "metadata": {
                "url": "https://example.com",
                "title": "Example Page"
            }
        }
        
        parsed_page = ParsedPage.from_json(minimal_data)
        assert isinstance(parsed_page, ParsedPage)
        assert len(parsed_page.actions.actions) == 0
        assert len(parsed_page.forms.forms) == 0
        assert parsed_page.metadata.url == "https://example.com"
        assert len(parsed_page.important_elements.elements) == 0

    def test_parsed_page_empty(self):
        """Test creating ParsedPage with empty data."""
        parsed_page = ParsedPage.from_json({})
        assert isinstance(parsed_page, ParsedPage)
        assert len(parsed_page.actions.actions) == 0
        assert len(parsed_page.forms.forms) == 0
        assert parsed_page.metadata.url == ""
        assert len(parsed_page.important_elements.elements) == 0

    def test_parsed_page_helpers(self):
        """Test ParsedPage helper methods."""
        page_data = {
            "actions": [
                {
                    "tag": "button",
                    "attributes": {"class": "submit"},
                    "text": "Submit",
                    "rect": {"x": 100, "y": 200, "width": 150, "height": 40},
                    "interactive": True,
                    "type": "button",
                    "sensitive": False,
                    "role": None,
                    "aria": {},
                    "computedStyle": {},
                    "selector": "button.submit"
                },
                {
                    "tag": "input",
                    "attributes": {"type": "password"},
                    "text": "",
                    "rect": {"x": 100, "y": 300, "width": 200, "height": 40},
                    "interactive": True,
                    "type": "password",
                    "sensitive": True,
                    "role": None,
                    "aria": {},
                    "computedStyle": {},
                    "selector": "input[type='password']"
                }
            ],
            "forms": [
                {
                    "id": "login-form",
                    "action": "/login",
                    "method": "post",
                    "fields": [
                        {
                            "type": "email",
                            "name": "email",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "search-form",
                    "action": "/search",
                    "method": "get",
                    "fields": [
                        {
                            "type": "text",
                            "name": "q",
                            "required": False
                        }
                    ]
                }
            ],
            "metadata": {
                "url": "https://example.com",
                "canonical": "https://example.com/canonical",
                "title": "Example Page",
                "meta": {
                    "description": "Test page description",
                    "og": {
                        "title": "OG Title",
                        "description": "OG Description",
                        "image": "https://example.com/image.jpg"
                    }
                },
                "status": "complete"
            },
            "important_elements": [
                {
                    "tag": "button",
                    "text": "Submit",
                    "type": "button",
                    "selector": "button.submit",
                    "isInteractive": True,
                    "hasClickHandler": True,
                    "isFocusable": True,
                    "ariaRole": "button",
                    "importance_score": 0.9
                },
                {
                    "tag": "div",
                    "text": "Content",
                    "type": "div",
                    "selector": "div.content",
                    "isInteractive": False,
                    "hasClickHandler": False,
                    "isFocusable": False,
                    "ariaRole": None,
                    "importance_score": 0.3
                }
            ]
        }
        
        parsed_page = ParsedPage.from_json(page_data)
        
        # Test basic getter methods
        actions = parsed_page.get_actions()
        assert len(actions) == 2
        assert actions[0].tag == "button"
        assert actions[1].tag == "input"
        
        forms = parsed_page.get_forms()
        assert len(forms) == 2
        assert forms[0].id == "login-form"
        assert forms[1].id == "search-form"
        
        metadata = parsed_page.get_metadata()
        assert metadata.url == "https://example.com"
        assert metadata.title == "Example Page"
        
        important_elements = parsed_page.get_important_elements()
        assert len(important_elements) == 2
        assert important_elements[0].tag == "button"
        assert important_elements[1].tag == "div" 