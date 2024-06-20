import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property string imagePath/*: "https://lastfm.freetls.fastly.net/i/u/770x0/d2da6c1d060adc621b087c1189d18a2f.jpg"*/
    property string songTitle/*: "Song Title"*/
    property string artist/*: "Artist Name"*/
    property string album/*: "Album Name"*/



    RowLayout {
        id: layout
        width: parent.width
        height: parent.height
        spacing: 6

        Image {
            id: image
            source: root.imagePath
            fillMode: Image.PreserveAspectFit
            
            Layout.preferredWidth: 150
            Layout.preferredHeight: 150
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
        }

        Rectangle {
            id: details
            Layout.fillWidth: true
            color: "red"
            
            Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter

            Text {
                id: title
                anchors.top: parent.top
                text: root.songTitle
            }

            Text {
                id: artist
                anchors.top: title.bottom
                text: root.artist
            }
        }
    }
}