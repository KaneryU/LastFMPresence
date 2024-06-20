import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
            root.mainModel = model
        }
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
    
    
    ListView {
        id: listView
        anchors.fill: parent
        model: root.mainModel
        
        delegate: songItemDelagate
    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton {
                text: "Pause"
                icon.name: "pause"
                onClicked: {
                    // Add your action here
                }
            }
            ToolButton {
                text: "Exit"
                icon.name: "exit"
                onClicked: {
                    // Add your action here
                }
            }
            ToolButton {
                text: "Resume"
                icon.name: "resume"
                onClicked: {
                    // Add your action here
                }
            }
            ToolButton {
                text: "Force Refresh"
                icon.name: "forcerefresh"
                onClicked: {
                    // Add your action here
                }
            }
            ToolButton {
                text: "Change User"
                icon.name: "changeuser"
                onClicked: {
                    // Add your action here
                }
            }
            ToolButton {
                text: "Clear List"
                icon.name: "clearlist"
                onClicked: {
                    // Add your action here
                }
            }
        }
    }

    footer: Item {
        height: 20
        Rectangle {
            anchors.fill: parent
            color: "transparent"
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