
async function deleteMessage(id) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/message/${id}/`,
          {method: "DELETE", mode: 'same-origin',
           headers: {'X-CSRFToken': csrftoken}
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("HTTP status " + response.status);
        }
        document.getElementById(id).remove();
    })
    .catch(err => {
        document.getElementById(id).querySelector('.error').innerHTML = "Error: delete failed";
    });
}
