
# Customisation guide

This is intended to be an extremely basic guide to customising basic features of the default platform. 

## Aesthetics

**Progress Timer**
There is a default progress timer in the chat interface sidebar. You can edit this timer be changing the following:
Relevant code locations:
`templates/chat.html` under id=progress
'static/js/chat.js' under label // Progress Timer     (note: to change the length of the timer see the set number on the bottom line)
'statc/css/styles.css' under label // Progress Timer


## Sidebar Measures

**End of Interaction Button**
The button in the chat.html with id="reset" has an event listener in the chat.js file. When this button appears is controlled by this event listener (i.e., resetButton.addEventListener). Whether this button appears on every interaction or every nth interaction is controlled by the resetCount cookie statements in this event listener. By default these statements set the extra command instructions and command prompt buttons to appear on the second interaction. 


