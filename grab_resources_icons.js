// Grab icons from https://deeptownguide.com/Items using DevConsole
var imgs = $x("//tr[@role='row']//img")
var result = ""
for (img in imgs) {
    result = result + "\n" + imgs[img].currentSrc
}