// Authors: Tommaso Galati (tommasogalati01@gmail.com) - Giovanni Cavallaro (cavaterza89@gmail.com)
var generalcontext = {
    renderEverything: true,   
    block_length: 50,
    minimum_errorpage_threshold: 60, 
    msg_toomanypages: "The dataset contains " + $('#hidden_page_number').text()  + " pages and the loading time can be excessive . \n Do you want to load only pages with any errors?"


}



$( document ).ready(function() {
    pagesInitialize();
    change_content_color(1);
    $('.chpage').click(function() {
        var num_page = $(this).text();
        var current_page = $('div.page.active').attr('id').replace('page-', '');
        if($('#page-'+num_page).length) {
            $('#page-'+current_page).removeClass('active');
            $('#page-'+num_page).addClass('active');
            $('button.chpage.active').removeClass('active');
            $(this).addClass('active');
        }
    });
    $('#exportcsv').click(exportCsv);
    $('#buttonerrorformat').click(downloadTemplateCSV);
});


var total_pages = 0;
var page_loaded = 0;
var count = 2;


function pagesInitialize(){
    if ($('#hidden_page_number').text() > generalcontext.minimum_errorpage_threshold){
        createModalButton()    
    }
    else{
        loadAllThePages(true)
    }
    //call visualization for each page
}

function loadAllThePages(re) {
    generalcontext.renderEverything = re;
    console.log("render§: " + generalcontext.renderEverything)

    var page_number = $('#hidden_page_number').text();
    page_loaded = page_number;
    total_pages  = page_number;

    console.log("page number: " + page_number)

    if(page_number > 1) {
        var blockLength = generalcontext.block_length;
        var factory = check_for_next_block_cl(page_number)

         //false if page_number is above a certain threshold; the threshold is obviously a magic number.

        pageUpdate(2, factory);
    }
    else{
        loadingComplete();
    }
}


function createModalButton(){
    var html = '<div class="modal fade" id="alert-choose" role="dialog" style="width: 300px">' +
        '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content">' +
                '<div class="modal-header">' +
                    '<h4 class="modal-title">Avviso</h4>' + 
                '</div>' + 
                '<div class="modal-body">' + 
                    '<p>' + generalcontext.msg_toomanypages +' </p>' + 
                '</div>' + 
                '<div class="modal-footer">' + 
                    '<button type="button" class="btn btn-default" id="justerror-button" onclick="loadAllThePages(false)" data-dismiss="modal">Just errors</button>' + 
                    '<button type="button" class="btn btn-default" id="everything-button" onclick="loadAllThePages(true)" data-dismiss="modal">Load the whole dataset</button>' +
                '</div>' + 
            '</div>' + 
        '</div>' +  
    '</div>';

    $('#page_container').append(html);
    $("#alert-choose").modal()
}





function create_block_cl(numOfPages){
    var numberOfPages = numOfPages;
	var blockLenght = generalcontext.block_length;

    console.log("bl: " + generalcontext.block_length)

	var indexOfBlock = 0;

	var count = 0;
	var threshold = blockLenght;


	function pageupdate_callback(){
		count++;
        if(count >= numberOfPages){
            return;
        }

		console.log("count: " + count)
		if(count==threshold){
			threshold += blockLenght;
			console.log("-- starting new block; new threshold: " + threshold)
			cb();
		}

	}

	function cb(){
		console.log("executing cb: " + blockLenght)
		for (var j = 1; j <= blockLenght; j++){
            if (!((j + (blockLenght*indexOfBlock)) === 1)){
    			pageUpdate(j + (blockLenght*indexOfBlock), pageupdate_callback);
		        console.log("requested page: " + (j + blockLenght*indexOfBlock)) 
            }else{
                count++;
            }
	   }
       indexOfBlock++;
    }
	return cb;
}
function check_for_next_block_cl(numOfPages){
	var fm = create_block_cl(numOfPages)
	console.log("check for next block initialized.....")

	var count = 0;
	var threshold = fm.blockLenght;

	function cfnb(){
		count++;
		console.log("count: " + count)
		if(count==threshold){
			threshold += fm.blockLenght;
			console.log("starting new block; new threshold: " + threshold)
			fm();
		}
	}
	fm.page_update_callback = cfnb
	fm();
	return cfnb;
}


//creates an array of as many elements as the result of the division between the number of pages and the block length, and every element will be an index of a block
function createBlocks(page_number,blockLength){
	var nBlocks = Math.ceil(page_number/blockLength);
	var blocks = []
	for (i = 0; i < nBlocks-1; i++){
		blocks[i] = blockLength;
	}
	blocks[nBlocks-1] = page_number - (blockLength*(nBlocks-1));
	return blocks
}



function pageUpdate(numpage, checkfornextblock){
	
	console.log(typeof(checkfornextblock))

    //get the value for a single page with an API call
    var offset = (numpage-1)*15;
    var data_to_upoad = {'resource_id': $('#hidden_id').text(), 'offset':offset };
    var ckan_url = $('#hidden_ckan_url').text();
    var insert_url = ckan_url + '/api/action/get_pagination_data'; //'http://192.168.242.128/api/action/get_pagination_data' ; //
    $.ajax({
        url: insert_url,
        method: 'POST',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },

        data: JSON.stringify(data_to_upoad),

        success: function(data, textStatus, jqXHR) {
            console.log("success")
            var found_invalid_record = false;
            for (var j = 0; j < data.result.record_to_render.length; j++){
                for(var p in data.result.record_to_render[j] ){
                    if (data.result.record_to_render[j].hasOwnProperty(p)){
                        if(data.result.record_to_render[j][p].valid === 2){
                            found_invalid_record = true;
                        }
                    }
                }
            }
            if (generalcontext.renderEverything){
                ajaxresponse(data, textStatus, jqXHR, numpage, offset)
            }
            else if(!generalcontext.renderEverything && found_invalid_record){ // there are some validation error and you have to display the page so that the user can correct them
                if(!$('#error-display-aside').length){
                    $('#selectContainer').after($('<div></div>').addClass('btn-group').attr('id', 'error-display-aside').attr('style', 'padding: 0 15px 25px 10px; margin:10px auto; max-width:90%; overflow-x:scroll; overflow-y: hidden').append($('<h6></h6>').text('Pages with possible validation errors')))
                    $('#error-display-aside').append($('<div ></div>').attr('id','loading-error-div').attr('style', 'border: 10px solid #f3f3f3; border-top: 10px solid #3498db; border-radius: 50%;width: 10px;height: 10px;margin: 5px;animation: spin 2s linear infinite;'))

                    $('#savebutton').prop('disabled', false);
                    $('#savebutton').removeClass('disabled');

                }
                $('#error-display-aside').append($('<button></button>').text(numpage).addClass("chpage btn btn-secondary").click(function() {
                                        var num_page = $(this).text();
                                        var current_page = $('div.page.active').attr('id').replace('page-', '');
                                        if($('#page-'+num_page).length) {
                                            $('#page-'+current_page).removeClass('active');
                                            $('#page-'+num_page).addClass('active');
                                            $('button.chpage.active').removeClass('active');
                                            $(this).addClass('active');
                                        }
                                    }));
                ajaxresponse(data, textStatus, jqXHR, numpage, offset)   
            }
            else{ 
                $('button.chpage').filter(function() {
                    return $(this).text() == numpage.toString();
                }).css('background-color', 'green')
            }


            page_loaded--;        
            checkfornextblock()
            console.log("pages loaded: " + page_loaded)
            if(page_loaded == 0) { //todo: questo dovrà essere cambiato, oppure pageloaded dovrà essere inizializzato al numero di pagine fin da subito.
                loadingComplete();
            }
        },
        error: function (jqXHR, textStatus, errorThrown) { 
            console.log(textStatus); 
            console.log(errorThrown);
            checkfornextblock()
        }
    });
}

function ajaxresponse(data, textStatus, jqXHR, numpage, offset){
    var text = '<div id="page-'+numpage+'" class="page">'+
        '<div class="listcontainer">'+
            '<table class="table table-bordered tabled" id="tabledata-'+numpage+'">'+
               '<thead>'+ $('#page-1 thead').html() +'</thead><tbody>';

    for(i=0; i<data.result.record_to_render.length; i++){
        var index = ((i+1)+offset);
        text +='<tr data-row="'+index+'">'+
            '<td class="valid-0 num-row">'+index+'</td>'+
            '<td class="valid-0 select-row-del"><input type="checkbox" value="" data-row="'+index+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].otherCategoryITA.valid+'"><input id="othercategoryita-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].otherCategoryITA.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].otherCategoryENG.valid+'"><input id="othercategoryeng-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].otherCategoryENG.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].nameITA.valid+'"><input id="nameita-'+index+'" type="text" class="nameita form-control" value="'+data.result.record_to_render[i].nameITA.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].nameENG.valid+'"><input id="nameeng-'+index+'" type="text" class="nameeng form-control" value="'+data.result.record_to_render[i].nameENG.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].abbreviationITA.valid+'"><input id="abbrevita-'+index+'" type="text" class="abbrevita form-control" value="'+data.result.record_to_render[i].abbreviationITA.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].abbreviationENG.valid+'"><input id="abbreveng-'+index+'" type="text" class="abbreveng form-control" value="'+data.result.record_to_render[i].abbreviationENG.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].descriptionShortITA.valid+'"><input id="descriptionshortita-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].descriptionShortITA.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].descriptionShortENG.valid+'"><input id="descriptionshorteng-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].descriptionShortENG.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].descriptionLongITA.valid+'"><input id="descriptionlongita-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].descriptionLongITA.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].descriptionLongENG.valid+'"><input id="descriptionlongeng-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].descriptionLongENG.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].phone.valid+'"><input id="phone-'+index+'" type="text" class="phone form-control" value="'+data.result.record_to_render[i].phone.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].fax.valid+'"><input id="fax-'+index+'" type="text" class="fax form-control" value="'+data.result.record_to_render[i].fax.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].url.valid+'"><input id="url-'+index+'" type="text" class="url form-control" value="'+data.result.record_to_render[i].url.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].email.valid+'"><input id="email-'+index+'" type="text" class="email form-control" value="'+data.result.record_to_render[i].email.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].RefPerson.valid+'"><input id="refperson-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].RefPerson.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].province.valid+'">'+
                '<div class="contlistprovince" id="contprovince-'+index+'">'+
                    '<input id="province-'+index+'" type="text" class="province form-control" value="'+data.result.record_to_render[i].province.value+'">'+
                '</div>'+
            '</td>'+
            '<td class="valid-'+data.result.record_to_render[i].city.valid+'">'+
                '<div class="contlistcity" id="contcity-'+index+'">'+
                    '<input id="city-'+index+'" type="text" class="city form-control" value="'+data.result.record_to_render[i].city.value+'">'+
                '</div>'+
            '</td>'+
            '<td class="valid-'+data.result.record_to_render[i].postalcode.valid+'">'+
                '<div class="contlistpostalcode" id="contpostalcode-'+index+'">'+
                    '<input id="postalcode-'+index+'" type="text" class="postalcode form-control" value="'+data.result.record_to_render[i].postalcode.value+'">'+
                '</div>'+
            '</td>'+
            '<td class="valid-'+data.result.record_to_render[i].streetAddress.valid+'"><input id="streetaddress-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].streetAddress.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].civicNumber.valid+'"><input id="civicnumber-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].civicNumber.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].secondPhone.valid+'"><input id="secondphone-'+index+'" type="text" class="secondphone form-control" value="'+data.result.record_to_render[i].secondPhone.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].secondFax.valid+'"><input id="secondfax-'+index+'" type="text" class="secondfax form-control" value="'+data.result.record_to_render[i].secondFax.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].secondEmail.valid+'"><input id="secondemail-'+index+'" type="text" class="secondemail form-control" value="'+data.result.record_to_render[i].secondEmail.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].secondStreetAddress.valid+'"><input id="secondstreetaddress-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].secondStreetAddress.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].secondCivicNumber.valid+'"><input id="secondcivicnumber-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].secondCivicNumber.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].notes.valid+'"><input id="notes-'+index+'" type="text" class="form-control" value="'+data.result.record_to_render[i].notes.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].timetable.valid+'"><input id="timetable-'+index+'" type="text" class="form-control " value="'+data.result.record_to_render[i].timetable.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].photo.valid+'"><input id="photo-'+index+'" type="text" class="photo form-control" value="'+data.result.record_to_render[i].photo.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].latitude.valid+'"><input id="lat-'+index+'" type="text" class="latitude form-control" value="'+data.result.record_to_render[i].latitude.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].longitude.valid+'"><input id="lon-'+index+'" type="text" class="longitude form-control" value="'+data.result.record_to_render[i].longitude.value+'"></td>'+
            '<td class="valid-'+data.result.record_to_render[i].streetId.valid+'"><input id="streetId-'+index+'" type="text" class="streetId form-control" value="'+data.result.record_to_render[i].streetId.value+'"></td>'+
        '</tr>';
    }

    text += '</tbody></table><div id="btn-delete-'+numpage+'" class="btn-delete">'+
        '<button id="trash-'+numpage+'" class="trash" data-toggle="tooltip" data-placement="top"' +
            'title="Elimina le righe selezionate" onclick="do_delete()">'+
            '<i class="fa fa-trash-o" aria-hidden="true"></i> Elimina</button>'+
        '<div id="trash-confirm-'+numpage+'" class="trash-confirm arrow_box"><p>Sei sicuro?</p>' +
        '<button onclick="confirm_delete(1)" class="btn btn-secondary">Sì</button>' +
        '<button onclick="confirm_delete(0)" class="btn btn-secondary">No</button>'+
        '</div></div></div></div>';
    $('#page_container').prepend(text);
    if($('.tabled .select-row-del').hasClass('show')) {
        $('#tabledata-'+numpage+' .select-row-del').addClass('show');
    }
    change_content_color(numpage);
    addListeners('#tabledata-'+numpage);

    changeRecordsNumber(data.result.records_id);
    $('button.chpage').filter(function() {
        return $(this).text() == numpage.toString();
    }).removeClass('disabled');
    $('button.chpage').filter(function() {
        return $(this).text() == numpage.toString();
    }).prop("disabled", false);
}

function loadingComplete(){
    $('#validatebutton').removeClass('disabled');
    $('#savebutton').removeClass('disabled');
    $('#exportcsv').removeClass('disabled');
    $('#addrow').removeClass('disabled');
    $('#deleterow').removeClass('disabled');
    $('#validatebutton').prop("disabled", false);
    $('#savebutton').prop("disabled", false);
    $('#exportcsv').prop("disabled", false);
    $('#addrow').prop("disabled", false);
    $('#deleterow').prop("disabled", false);

    var txt = '<strong>Informazione</strong> Tutti i dati presenti nella risorsa sono stati caricati.';
    txt += '<a href="#" class="close" data-dismiss="alert" aria-label="close" title="close">×</a>';
    $('.ckanext-datapreview .alert-warning').removeClass('alert-warning').addClass('alert-success').text('').append(txt);
    
}

function change_content_color(numpage) {
    //change color of page number
    var page_color = 1;
    $('#page-'+numpage+' .tabled tbody tr').each(function() {
        var row_color = 1;
        $(this).children('td').each(function() {
            var input_class = $(this).attr('class');
            if(input_class !== undefined && input_class.indexOf('valid-2') !== -1) {
                page_color = 2;
                row_color = 2;
            }
        });
        if(row_color == 1) {
            $(this).children('.num-row').css('background-color', 'white');
        } else {
            $(this).children('.num-row').css('background-color', '#f7a891');
        }
    });

    if(page_color == 1) {
        $('button.chpage').filter(function() {
                return $(this).text() == numpage.toString();
            }).children().css('background-color', '#29ce29');
    } else if(page_color == 2) {
        $('button.chpage').filter(function() {
                return $(this).text() == numpage.toString();
            }).children().css('background-color', '#f7a891');
    }
}

function changeRecordsNumber(newRecords){
    //change id record for each row
    var cleanedText = $('#hidden_number').text().replace(/\s/g, "").replace('[','').replace(']','');
    var oldNumber = cleanedText.split(',');
    for (var i=0; i<oldNumber.length; i++){
         oldNumber[i] = parseInt(oldNumber[i]);
    }
    oldnumber = oldNumber.sort();
    for(i=0; i<newRecords.length; i++){
        oldNumber.push(newRecords[i]);
    }
    var text = '[ ';
    for(i=0; i<oldNumber.length; i++){
        if(i != oldNumber.length-1){
            text += oldNumber[i]+', '
        }else{
            text += oldNumber[i]+' ]'
        }
    }
    $('#hidden_number').text(text);
}

function exportCsv() {
    //export csv
    $('#validatebutton').prop("disabled", true);
    $('#savebutton').prop("disabled", true);
    $('#exportcsv').prop("disabled", true);
    $('#validatebutton').addClass('disabled');
    $('#savebutton').addClass('disabled');
    $('#exportcsv').addClass('disabled');
    var keys = Array();
    var records = Array();
    $('#tabledata-1 thead tr th:not(:first)').each(function() {
        keys.push($(this).text().replace('*','').replace(/\s+/g, ''));
    });

    var iter = 0;
    for(var i = 1; i <= parseInt($('#hidden_page_number').text()); i++) {
        $('#tabledata-'+i.toString()).children('tbody').children('tr').each(function(){
            var obj = {};
            for(var i=0; i< keys.length; i++) {
                if(keys[i] == 'city' || keys[i] == 'province' || keys[i] == 'postalcode') {
                    obj[keys[i]] = $(this).children('td').eq(i+1).children('div').children('input').val();
                } else {
                    obj[keys[i]] = $(this).children('td').eq(i+1).children('input').val();
                }
            }
            records.push(obj);
        });
    }

    var csv = convertArrayOfObjectsToCSV({
        data: records
    });
    if(csv == null) return;
    var filename = $('.page-heading').text().toLowerCase().replace('.xlsx', '.csv').replace('.xls', '.csv');
    if(filename.indexOf('.csv') == -1) {
        filename += '.csv'
    }
    if(!csv.match(/^data:text\/csv/i)) {
        csv = 'data:text/csv;charset=utf-8,' + csv;
    }
    var data = encodeURI(csv);
    var link = document.createElement('a');
    link.setAttribute('href', data);
    link.setAttribute('download', filename);
    link.click();

    insert_data(true, false);
    setTimeout(function(){
        $('#exportcsv').prop("disabled", false);
    }, 2000);
}

function downloadTemplateCSV() {
    //create csv template and download
    var records = [];
    records.push({"Scegli": '', "otherCategoryITA": '', "otherCategoryENG": '', "nameITA": '', "nameENG": '',
                    "abbreviationITA": '', "abbreviationENG": '', "descriptionShortITA": '', "descriptionShortENG": '',
                    "descriptionLongITA": '', "descriptionLongENG": '', "phone": '', "fax": '', "url": '', "email": '',
                    "RefPerson": '', "province": '', "city": '', "postalcode": '', "streetAddress": '',
                    "civicNumber": '', "secondPhone": '', "secondFax": '', "secondEmail": '', "secondCivicNumber": '',
                    "secondStreetAddress": '', "notes": '', "timetable": '' , "photo": '', "latitude": '',
                    "longitude": '', "streetId": ''});
    var csv = convertArrayOfObjectsToCSV({
        data: records
    });
    if(csv == null) return;
    var filename = 'template.csv';
    if(!csv.match(/^data:text\/csv/i)) {
        csv = 'data:text/csv;charset=utf-8,' + csv;
    }
    var data = encodeURI(csv);

    var link = document.createElement('a');
    link.setAttribute('href', data);
    link.setAttribute('download', filename);
    link.click();
}

function convertArrayOfObjectsToCSV(args) {
    //convert array to csv
    var result, ctr, keys, columnDelimiter, lineDelimiter, data;

    data = args.data || null;
    if(data == null || !data.length) {
        return null;
    }

    columnDelimiter = args.columnDelimiter || ';';
    lineDelimiter = args.lineDelimiter || '\n';

    keys = Object.keys(data[0]);
    var index = keys.indexOf('Scegli');
    keys.splice(index, 1);

    result = '';
    result += keys.join(columnDelimiter);
    result += lineDelimiter;

    data.forEach(function(item) {
        ctr = 0;
        keys.forEach(function(key) {
            if(ctr > 0) result += columnDelimiter;
            result += '"' + item[key].toString() + '"';
            ctr++;
        });
        result += lineDelimiter;
    });

    return result;
}
