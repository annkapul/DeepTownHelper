var dict = {};
for (x in rows) {
//    if (x>5) { break;}
    var row = rows[x];
    tds = row.getElementsByTagName("td");
    for ( td in tds) {

        element = tds[td]
        console.log("td = ", td)
        if ( td == 0 ) {
            index = tds[td].innerText.replaceAll("\n", "")
            dict[index]= {}
//            console.log("Create index", index)
            }
        else {
            if (element.innerText == undefined || element.innerText.trim().length == 0) { break; }
            element_info = element.innerText.trim().split("\n")
            name = element_info[0].toLowerCase().replaceAll(" ", "_")
            value = element_info[1].replace("%", "").trim()
            dict[index][name] = value
//            console.log("Add element", name, value)
        }
    }
}
console.log(dict)
JSON.stringify(dict)