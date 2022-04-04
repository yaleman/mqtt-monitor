""" testing that pydantic loads and runs some stuff """


from mqtt_monitor import UserData, ConfigFile


def test_user_data() -> None:
    """tests a userdata object will parse"""

    foobar: UserData = {
        "hostname" : "example.com",
        "port" : "5000",
        "topics": [ "foo", "bar" ],
        "keepalives" : 59,
    }

    assert foobar["port"] == "5000"


    config = ConfigFile.parse_obj(foobar)
    assert config.port == 5000
    assert config.hostname == "example.com"
