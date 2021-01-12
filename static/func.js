async function post(url) {
    console.log("add_button I'm ALIVE");
    let response = await fetch
        (url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
         });

    if (response.ok) {
      let json = await response.json();
      console.log('Success:', JSON.stringify(json));
    } else {
      alert("HTTP Error" + response.status);
    }
}
