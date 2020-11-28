var progress = document.getElementById("progress");
var progress_wrapper = document.getElementById("progress_wrapper");
var progress_status = document.getElementById("progress_status");
var upload_btn = document.getElementById("upload_btn");
var loading_btn = document.getElementById("loading_btn");
var cancel_btn = document.getElementById("cancel_btn");
var alert_wrapper = document.getElementById("alert_wrapper");
var input = document.getElementById("file_input");
var file_input_label = document.getElementById("file_input_label");
//var icr_btn = document.getElementById("icr_btn");
var text_icr = document.getElementById("text_icr");

input.onchange = function(e) {
  // Creamos el objeto de la clase FileReader
  let reader = new FileReader();
  // Leemos el archivo subido y se lo pasamos a nuestro fileReader
  reader.readAsDataURL(e.target.files[0]);
  // Le decimos que cuando este listo ejecute el código interno
  reader.onload = function(){
    let preview = document.getElementById('preview'),
            image = document.createElement('img');
    image.src = reader.result;
    image.classList.add("img-responsive")
    preview.innerHTML = '';
    /*preview.innerHTML = `
    <img class="img-responsive" src="${reader.result}" alt="preview">
    `;*/
    preview.append(image);
    upload_btn.classList.remove("d-none");
    text_icr.innerHTML = '';
  };
}

function show_alert(message, alert){
    alert_wrapper.innerHTML = `
        <div class="alert alert-${alert} alert-dismissible fade show" role="alert">
        <span>${message}</span>
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        `
};
function show_alert_icr(message,textICR,alert){
    alert_wrapper.innerHTML = `
        <div class="alert alert-${alert} alert-dismissible fade show" role="alert">
        <span>${message}</span>
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        `
    text_icr.innerHTML = `
        <p>${textICR}</p>
        `
    upload_btn.classList.add("d-none");
};

function input_filename(){
    file_input_label.innerHTML = input.files[0].name;
}

function upload(url){
    console.log(url);
    if(!input.value){
        show_alert("No file selected","warning");
        return ;
    }
    var data = new FormData();
    var request = new XMLHttpRequest();
    request.responseType = "json";

    alert_wrapper.innerHTML = "";
    text_icr.innerHTML = "";
    input.disabled = true;
    upload_btn.classList.add("d-none");
    loading_btn.classList.remove("d-none");
    cancel_btn.classList.remove("d-none");
    progress_wrapper.classList.remove("d-none");
    //icr_btn.classList.remove("d-none");

    var file = input.files[0];
    var filename = file.name;
    var filesize = file.size;
    document.cooke = `filesize=$(filesize)`;
    data.append("file",file);

    request.upload.addEventListener("progress",function(e){
        var loaded = e.loaded;
        var total = e.total;

        var percentage_complete = (loaded/total) * 100;
        progress.setAttribute("style",`width: ${Math.floor(percentage_complete)}%`);
        progress_status.innerText = `${Math.floor(percentage_complete)}% cargado`

    })

    request.addEventListener("load",function(e){
        if(request.status == 200){
            show_alert_icr(`${request.response.message}`,`${request.response.textICR}`,"success");
        }else{
            show_alert(`Error uploading file`,"danger");
        }
        reset();
    })

    request.addEventListener("error",function(e){
        reset();
        show_alert("Error uploading file","danger")
    })

    request.addEventListener("abort",function(e){
        //reset();
        show_alert("Upload Cancel","primary")
        upload_btn.classList.remove("d-none");
        cancel_btn.classList.add("d-none");
        loading_btn.classList.add("d-none");
        progress_wrapper.classList.add("d-none");
        progress.setAttribute("style","width:0%");
        file_input_label.innerText = "Select file";
    })

    request.open("post",url);
    request.send(data);

    cancel_btn.addEventListener("click",function(){
        request.abort();
    })

}

function reset(){
    input.value = null;
    input.disabled = false;
    cancel_btn.classList.add("d-none");
    loading_btn.classList.add("d-none");
    //upload_btn.classList.remove("d-none");
    progress_wrapper.classList.add("d-none");
    progress.setAttribute("style","width:0%");
    file_input_label.innerText = "Select file";
}





