import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import "./qml/" as Kyu



ApplicationWindow {
    id: root
    visible: true
    width: 640
    height: 480
    title: "Last FM Rich Presence"
    property QtObject mainModel // absract list model from python
    property QtObject backend
    
    Connections {
        target: backend

        function onModelChanged(model) {
            mainModel = model
        }

        function onStatusChanged(status_) {
            print(status_)
            status.text = status_
        }
    }

    onClosing: function(close) {
        close.accepted = false
        backend.minimize()
    }

    MenuBar {
        id: menuBar

        Menu {
            id: mainMenu
            title: "Actions"

            MenuItem {
                property Action action: actions.actions[0]
                text: action.text
                onTriggered: action.trigger()
            }

            MenuItem {
                property Action action: actions.actions[1]
                text: action.text
                onTriggered: action.trigger()
            }

            MenuItem {
                property Action action: actions.actions[2]
                text: action.text
                onTriggered: action.trigger()
            }

            MenuItem {
                property Action action: actions.actions[3]
                text: action.text
                onTriggered: action.trigger()
            }

            MenuItem {
                property Action action: actions.actions[4]
                text: action.text
                onTriggered: action.trigger()
            }

            MenuItem {
                property Action action: actions.actions[5]
                text: action.text
                onTriggered: action.trigger()
            }
        }
    }

    Kyu.Actions {
        id: actions
    }
    
    Component {
        id: songItemDelagate
        Kyu.SongItem {
            width: listView.width
            height: 50
            /* properties to set
            property string imagePath
            property string songTitle: "Song Title"
            property string artist: "Artist Name"
            property string album
            */
            songTitle: "Song Title"
            artist: "Artist Name"
            album: "Album Name"
            imagePath: "https://lastfm.freetls.fastly.net/i/u/500x500/5893899e415a3a88b4a06a0ca2c52c5b.jpg"
        }
    }
    
    ScrollView {
        anchors.fill: parent
        leftPadding: 10
        topPadding: 10

        ListView {
            id: listView
            model: root.mainModel
            spacing: 10

            delegate: Item {
                width: parent.width
                height: 150
                

                Kyu.SongItem {
                    width: parent.width
                    height: parent.height
                    songTitle: model.title
                    artist: model.artist
                    album: model.album
                    imagePath: model.imagePath
                }
            }

            add: Transition {
                NumberAnimation { properties: "opacity"; from: 0; to: 100; duration: 300; easing.type: Easing.InOutQuad}
            }

            addDisplaced: Transition {
                NumberAnimation { properties: "x,y"; duration: 300; easing.type: Easing.InOutQuad}
            }
        }
    }

    footer: Item {
        height: 20
        Rectangle {
            anchors.fill: parent
            Text {
                id: status

                height: 20
                text: "Last FM Rich Presence"
                anchors.left: parent.left
                anchors.leftMargin: 10
                color: "black"
            }
        }
    }
}

