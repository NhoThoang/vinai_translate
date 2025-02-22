var socket = io();
var tooltip = document.getElementById("tooltip");

document.addEventListener("mouseup", function(event) {
    let selectedText = window.getSelection().toString().trim();
    if (selectedText.length > 0) {
        socket.emit('text_selected', selectedText);
    }
});


// document.addEventListener("touchend", function(event) {
//     // Lấy văn bản được chọn
//     let selectedText = window.getSelection().toString().trim();
    
//     // Nếu có văn bản được chọn
//     if (selectedText.length > 0) {
//         // Gửi văn bản qua WebSocket
//         socket.emit('text_selected', selectedText);
//     }
// });

document.addEventListener2("click", function() {
    tooltip.style.display = "none"; // Ẩn tooltip khi click bất kỳ đâu
});


socket.on('text_ack', function(data) {
    console.log("Received from server:", data); 
    let selection = window.getSelection();
    if (selection.rangeCount > 0) {
        let range = selection.getRangeAt(0);
        let rect = range.getBoundingClientRect();

        tooltip.style.left = `${rect.left + window.scrollX}px`;
        tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 30}px`;
        tooltip.innerText = data.translated;
        tooltip.style.display = "block";
    }
});


document.addEventListener("click", function() {
    tooltip.style.display = "none";
});

function uploadFile() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];

    if (!file) {
        alert("Vui lòng chọn một file Word!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Lỗi: " + data.error);
        } else {
            document.getElementById("fileContent").innerText = data.text;
        }
    })
    .catch(error => console.error("Lỗi:", error));
}
