var c = function () {
    console.log.apply(console, arguments);
}

// GLOBAL VARS
var chart_data = {}, dump = {};
var pl_name = '';
var new_name = '';
var plid = '';

window.onload = function () {
    showDecades();
    getRandomChart();
}

createPL.addEventListener('click', confirmationModal);
createPL = document.getElementById('createPL');
createPL2 = document.getElementById('createPL2');
createPL2.addEventListener('click', editPlaylistName);
// loginBtn = document.getElementById('loginBtn');
// loginBtn.addEventListener('click', login);

function getRandomChart() {
    let plid = '';
    const url = '/random_chart';
    $.ajax({
        url: url,
        type: 'GET',
        data: { 'plid': plid },
        dataType: 'json',
        cache: false,
        success: function (data) {
            let plid = data[0];
            let decade = data[1];
            let year = data[2];
            showRandomChart(plid, decade, year);
        },
        error: function (response) {
            alert("Error getting data")
        },
    });
}

function showRandomChart(plid, decade, year) {
    $('#chooseWeek').val(plid).change()
    $('#chooseDecade').val(decade).change();
    $('#chooseYear').val(year).change();
}

function chartDetail() {
    let chart = document.querySelector('#chooseWeek').value;
    const url = '/chart_detail';
    $.ajax({
        url: url,
        type: 'GET',
        data: { 'chart': chart },
        dataType: 'json',
        success: function (data) {
            chart_data = data[0];
            pl_name = data[1];
            let html_data = '';
            for (const [key, value] of Object.entries(chart_data)) {
                let rank = (parseInt(value['track_id'].slice(8,), 10)),
                    name = (value['name']),
                    artist = (value['artist']),
                    img_url = (value['img_url']);
                html_data += `<div class="track-artist-container" value="${rank}"><img class="img_url"
                                    src="${img_url}" onError="this.onerror=null;this.src='/img/album.png';"</img>
                               <div class="track"><b>${name} - (${rank})</b><br/>${artist}</div>
                         </div>`
            }
            $("#showChart").html(html_data);
            deSelectTracks();
        },
    });
}

function login() {
    const url = '/login';
    console.log('JS LOGIN()');
    $.ajax({
        url: url,
        type: 'GET',
    });
}


function confirmationModal() {
    var modal = document.getElementById("confirmationModal");
    modal.style.display = "block";

    var div = document.getElementsByClassName("conf-modal-content")[0]
    div.onclick = function () {
        modal.style.display = "none";
    }

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
    getRandomChart();
}

// 6. Add Playlist to Spotify
function addPlaylistToApp() {
    let spot_ids = [];
    for (const [key, value] of Object.entries(chart_data)) {
        let spot_id = (value['spot_id'])
        spot_ids.push(spot_id)
    }
    console.log(spot_ids.length);
    const url = '/add_playlist_to_app';
    $.ajax({
        type: 'GET',
        data: {
            'spot_ids': spot_ids,
            'pl_name': new_name,
        },
        url: url,
        success: function () {
            var modal = document.getElementById("editPlaylistName");
            modal.style.display = "none";
            confirmationModal();
        },
        error: function (response) {
            alert('Error')
        }
    });
}

// 5. Change default name
function editPlaylistName() {
    var modal = document.getElementById("editPlaylistName");
    modal.style.display = "block";
    var input = document.getElementById('nameInput');
    input.placeholder = pl_name;
    input.setSelectionRange(0, 0);
    input.focus();

    var editNameBtn = document.getElementById('editNameBtn');
    editNameBtn.addEventListener("click", e => {
        new_name = document.getElementById('nameInput').value;
        if (new_name.length == 0) {
            new_name = pl_name;
        }
        console.log('new_name: ', new_name);
        addPlaylistToApp(chart_data, new_name);
    });

    // clicking X to close
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function () {
        modal.style.display = "none";

    }
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

// 4. Deselect unwanted tracks
function deSelectTracks() {
    // c(chart_data)
    document.querySelectorAll(".track-artist-container").forEach(item => {
        item.addEventListener('click', event => {
            let value = Number(item.getAttribute('value') - 1);
            if (value in chart_data) {
                dump[value] = chart_data[value];
                delete (chart_data[value]);
                console.log('Song removed. # of songs in dict: ', Object.keys(chart_data).length);
            } else {
                chart_data[value] = dump[value];
                delete (dump[value]);
                console.log('Song added. # of songs in dict: ', Object.keys(chart_data).length);
            }
            console.log('clicked value: ', value);
            const style = getComputedStyle(item);
            const bgColor = style.backgroundColor;
            if (bgColor === 'rgb(67, 67, 67)') {
                item.style.backgroundColor = 'rgb(0, 0, 0)';
                // item.style.backgroundColor = 'rgb(255, 102, 102)';
            }
            else {
                item.style.backgroundColor = 'rgb(67, 67, 67)';
            }
        })
    })
}


//dropdowns
function chooseYear() {
    let year = document.querySelector('#chooseYear').value;
    c('Hit chooseYear. Year: ', year)
    const url = '/show_weeks';
    $.ajax({
        url: url,
        type: 'GET',
        data: { 'year': year },
        dataType: 'json',
        success: function (data) {
            pl_name = 'name';
            let html_data = '';
            data.forEach(function (data) {
                html_data += `<option
    value="${data.playlist_id}">${data.name.slice(7,)}</option>`
            });
            $("#chooseWeek").html(html_data).change();
        },
        error: function (response) {
            alert("Error getting data")
        },
    });
}

function chooseDecade() {
    let decade = parseInt(document.querySelector('#chooseDecade').value),
        year = document.querySelector('#chooseYear');
    year.options.length = 0;
    let yearsArray = new Array();
    for (var i = 0; i < 10; i++) {
        yearsArray.push(decade)
        decade = decade + 1;
    }
    for (var i = 0; i < yearsArray.length; i++) {
        let option = document.createElement('option');
        option.innerHTML = yearsArray[i];
        option.value = yearsArray[i];
        if (option.value < 1952 || option.value > 2023) {
            option.remove()
        }
        else {
            year.appendChild(option);
        }
    }
    $('#chooseYear').change()
}

function showDecades() {
    const decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020];
    // let decade = document.querySelector('#chooseYear').value,
    let decadeSelect = document.querySelector('#chooseDecade');
    for (var i = 0; i < decades.length; i++) {
        var option = document.createElement('option');
        option.innerHTML = decades[i] + "'s";
        option.value = decades[i];
        decadeSelect.appendChild(option);
    }

}