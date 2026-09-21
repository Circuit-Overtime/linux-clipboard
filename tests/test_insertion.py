"""Direct insertion uses the text caret and UTF-8 byte length."""

from __future__ import annotations

from linux_dot_panel.insertion import TextInserter


class FakeText:
    def __init__(self) -> None:
        self.offset = 3

    def get_caret_offset(self) -> int:
        return self.offset

    def set_caret_offset(self, offset: int) -> bool:
        self.offset = offset
        return True


class FakeEditable:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str, int]] = []

    def insert_text(self, offset: int, value: str, length: int) -> bool:
        self.calls.append((offset, value, length))
        return True


class FakeTarget:
    def __init__(self) -> None:
        self.text = FakeText()
        self.editable = FakeEditable()

    def get_text_iface(self) -> FakeText:
        return self.text

    def get_editable_text_iface(self) -> FakeEditable:
        return self.editable


class FakeStates:
    def __init__(self, focused: bool) -> None:
        self.focused = focused

    def contains(self, state: str) -> bool:
        return self.focused and state == "focused"


class FakeNode:
    def __init__(self, *, focused=False, editable=False, role="text", children=()) -> None:
        self.focused = focused
        self.editable = editable
        self.role = role
        self.children = children

    def get_state_set(self) -> FakeStates:
        return FakeStates(self.focused)

    def is_editable_text(self) -> bool:
        return self.editable

    def get_role(self) -> str:
        return self.role

    def get_child_count(self) -> int:
        return len(self.children)

    def get_child_at_index(self, index: int) -> FakeNode:
        return self.children[index]


def test_insertion_uses_caret_and_preserves_target_for_repeated_emoji():
    inserter = TextInserter()
    target = FakeTarget()
    inserter.target = target

    assert inserter.insert("🚀")
    assert inserter.insert("🙂")
    assert target.editable.calls == [(3, "🚀", 4), (4, "🙂", 4)]
    assert target.text.offset == 5


def test_capture_skips_password_fields():
    password = FakeNode(focused=True, editable=True, role="password")
    text = FakeNode(focused=True, editable=True)
    root = FakeNode(children=(password, text))
    inserter = TextInserter()
    inserter.atspi = type(
        "FakeAtspi",
        (),
        {
            "StateType": type("StateType", (), {"FOCUSED": "focused"}),
            "Role": type("Role", (), {"PASSWORD_TEXT": "password"}),
            "get_desktop_count": staticmethod(lambda: 1),
            "get_desktop": staticmethod(lambda index: root),
        },
    )

    inserter.capture_focused_field()
    assert inserter.target is text
