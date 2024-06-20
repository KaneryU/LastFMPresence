import QtQuick
import QtQuick.Controls

Item {
    property list<Action> actions: [
            exitAction,
            pauseAction,
            resumeAction,
            forceRefreshAction,
            changeUserAction,
            clearListAction
    ]

    Action {
        id: exitAction
        text: "Exit"
        icon.name: "exit"
        onTriggered: {
            backend.exit();
        }
    }

    Action {
        id: pauseAction
        text: "Pause"
        icon.name: "pause"
        onTriggered: {
            backend.pause();
        }
    }

    Action {
        id: resumeAction
        text: "Resume"
        icon.name: "resume"
        onTriggered: {
            backend.resume();
        }
    }

    Action {
        id: forceRefreshAction
        text: "Force Refresh"
        icon.name: "forcerefresh"
        onTriggered: {
            backend.forceRefresh();
        }
    }

    Action {
        id: changeUserAction
        text: "Change User"
        icon.name: "changeuser"
        onTriggered: {
            backend.changeUser();
        }
    }

    Action {
        id: clearListAction
        text: "Clear List"
        icon.name: "clearlist"
        onTriggered: {
            backend.clearList();
        }
    }

}