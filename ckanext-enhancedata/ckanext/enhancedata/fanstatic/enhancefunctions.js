// Authors: Tommaso Galati (tommasogalati01@gmail.com) - Giovanni Cavallaro (cavaterza89@gmail.com)

$( document ).ready(function() {

    $('#category').change(function(){
        if( $(this).val() != 'empty' ) {
            changeCategory($(this).val());
        } else {
            changeCategory('empty');
        }
    });

    $('#categoryEng').change(function(){
       if( $(this).val() != 'empty' ) changeSubCategory($(this).val());
    });

    addListeners('#tabledata-1');

    initializeList();
    initializeMandatory();

    $('#addrow').on('click', addrow);
    $('#deleterow').on('click', deleterow);
    $('#validatebutton').on('click', function(){
        $('#validatebutton').prop("disabled", true);
        $('#savebutton').prop("disabled", true);
        $('#exportcsv').prop("disabled", true);
        $('#validatebutton').addClass('disabled');
        $('#savebutton').addClass('disabled');
        $('#exportcsv').addClass('disabled');
        checkValidate();
    });
    $('#savebutton').on('click', function() {
        $('#validatebutton').prop("disabled", true);
        $('#savebutton').prop("disabled", true);
        $('#exportcsv').prop("disabled", true);
        $('#validatebutton').addClass('disabled');
        $('#savebutton').addClass('disabled');
        $('#exportcsv').addClass('disabled');
        insert_data(true, true);
    });

    $('#category').selectpicker('val', $('#hidden_current_categ').text());
    $('#categoryEng').selectpicker('val', $('#hidden_current_subcateg').text());

     $("#inputModal").on("hidden.bs.modal", function () {
        var id = $('#callFrom').text();
        var numRow = id.split('-');
        if( numRow[0] == 'lat' || numRow[0] == 'lon' ){
            if($('#lat-'+numRow[1]).parent('td').hasClass('valid-1') && $('#lon-'+numRow[1]).parent('td').hasClass('valid-1') && $('#streetId-'+numRow[1]).val() == '') {
                $('#streetId-'+numRow[1]).attr('placeholder', 'Elaborazione toponimo in corso');
                get_toponimo(numRow[1]);
            }
        }
    });

   	$(window).bind('beforeunload',function(){
        if( $('#page_container').length>0) return confirm();
    });

    $('#inputModalField').on('input', function() {
        var elId = $('#callFrom').text();
        $('#'+elId).val($(this).val());
        $('#'+elId).trigger('input');
    });

});

function addListeners(tableid) {
    //handle listeners to add for every page
    $(tableid + ' .nameita,'+ tableid + ' .nameeng,' + tableid + ' .abbrevita,' + tableid + ' .abbreveng').on('input', function(){
        var text = $(this).val();
        $('#'+this.id).val($(this).val().toUpperCase());
    });

    $(tableid + ' .nameita').on('input', function(){
        if($(this).val() != '') {
            if($(this).parent().attr('class').indexOf('valid-2') !== -1) {
                $(this).parent().removeClass('valid-2');
                $(this).parent().addClass('valid-1');
            }
        } else {
            if($(this).parent().attr('class').indexOf('valid-1') !== -1) {
                $(this).parent().removeClass('valid-1');
            }
            if($(this).parent().attr('class').indexOf('valid-0') !== -1) {
                $(this).parent().removeClass('valid-0');
            }
            $(this).parent().addClass('valid-2');
        }
        change_content_color($(this).parents('.tabled').attr('id').replace('tabledata-',''));
    });

    $(tableid + ' .email,' + tableid + ' .secondemail').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_mail?email='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'email');
    });

    $(tableid + ' .phone,' + tableid + ' .secondphone').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_phonenumber?phone='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'phone');
    });

    $(tableid + ' .fax,' + tableid + ' .secondfax').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_phonenumber?phone='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'fax');
    });

    $(tableid + ' .url').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_url?url='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'url');
    });

    $(tableid + ' .photo').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_url?url='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'photo');
    });

    $(tableid + ' .latitude').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_latitude?latitude='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'latitude');
    });

    $(tableid + ' .longitude').on('input', function(){
       var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_longitude?longitude='+$(this).val();
       checkField(this.id, $(this).val(), urlrequest, 'longitude');
    });

    $(tableid + ' .city').on('click', function(){
        appendDropmenu(this, 'contlistcity', 'citylist', 'dropmenucity', false);
    });

    $(tableid + ' .province').on('click', function(){
       appendDropmenu(this, 'contlistprovince', 'provincelist', 'dropmenuprovince', false);
    });

    $(tableid + ' .postalcode').on('click', function(){
        appendDropmenu(this, 'contlistpostalcode', 'postalcodelist', 'dropmenupostalcode', false);
    });

    $(tableid + ' .city').on('input', function(){
        var text = $(this).val();
        $('#'+this.id).val($(this).val().toUpperCase());
        updateDropmenu(this, 'contlistcity', 'citylist', 'dropmenucity', false);
        $(this).parents('td').removeClass('valid-1').addClass('valid-2');
        $(this).focus();
    });

    $(tableid + ' .province').on('input', function(){
        var text = $(this).val();
        $('#'+this.id).val($(this).val().toUpperCase());
        updateDropmenu(this, 'contlistprovince', 'provincelist', 'dropmenuprovince', true);
        $(this).parents('td').removeClass('valid-1').addClass('valid-2');
        $(this).focus();
    });

    $(tableid + ' .postalcode').on('input', function(){
        updateDropmenu(this, 'contlistpostalcode', 'postalcodelist', 'dropmenupostalcode', false);
        $(this).focus();
    });

    $(tableid + '.tabled input').on('input', function () {
        $('#inputModalField').val($(this).val());
        overrideClass($(this));
    });

    $(tableid + '.tabled input:not(:checkbox)').click(function() {
        var el_classes = $(this).attr('class');
        if(el_classes.indexOf('province') !== -1 ||
            el_classes.indexOf('city') !== -1 || el_classes.indexOf('postalcode') !== -1) {
            return;
        }
        var idx = $(this).parent().index();
        idx = parseInt(idx) + 1;
        var name = $('.page.active .tabled thead tr th:nth-child('+idx.toString()+')').text();
        $('#inputModalLabel').text(name);
        $('#inputModalField').val($(this).val());
        overrideClass($(this));
        $('#callFrom').text($(this).attr('id'));
        $('#inputModal').modal();
    });

    update_toponimo(tableid);

}

function update_toponimo(tableid){
    //update toponimo for a page
    var array = [];
    $(tableid+' tbody tr').each(function(){
        var numRow = $(this).attr('data-row');
        if ( $('#lat-'+numRow).parent('td').hasClass('valid-1') && $('#lon-'+numRow).parent('td').hasClass('valid-1') && $('#streetId-'+numRow).val() == '' ){
            array.push(numRow);
            $('#streetId-'+numRow).attr('placeholder', 'Elaborazione toponimo in corso');
        }
    });
    get_toponimo_list(array);
}

function get_toponimo_list(numRow){
    //get toponimo for each row
    if( numRow.length != 0) get_toponimo(numRow[0]);
    numRow.shift();
    if( numRow.length != 0){
        setTimeout(function(){ get_toponimo_list(numRow)}, 3000);
    }
}

function initializeMandatory(){
    //initialize mandatory field with *
    $('.tabled th').each(function(){
        var value = $(this).text();
        if( value == 'nameITA' || value == 'province' || value == 'city' || value == 'latitude' || value == 'longitude' ){
            $(this).text( value+' *');
        }
    })
}

function overrideClass(jElement) {
    //hanlde connection from modal to input in row
    var parent_class = jElement.parent().attr('class');
    var idx = parent_class.indexOf('valid');
    if(idx !== 1) {
        var class_to_append = parent_class.slice(idx, idx+7);
        if($('#inputModalField').attr('class').indexOf(class_to_append) == -1) {
            var modal_classes = $('#inputModalField').attr('class');
            var modal_idx = modal_classes.indexOf('valid');
            if(modal_idx !== -1) {
                var old_class = modal_classes.slice(modal_idx, modal_idx+7);
                $('#inputModalField').removeClass(old_class);
            }
            $('#inputModalField').addClass(class_to_append);
        }
    }
    setTimeout(function(){
        $('#inputModalField').focus();
    },900);
}

function updateDropmenu(obj, contlist, listtype, droptype, isprovince){
    //update dropmenu list in the triple province-city-postalcode
    var textValue = $(obj).val();
    var idcont = $(obj).parent('.'+contlist).attr('id');

    $('#'+idcont+' .dropmenu div').remove();
    if(textValue.length > 1 || isprovince){
        var inputregex = new RegExp('^'+textValue, 'i');

        if(isprovince){
            div = 'div';
        }else{
            div = 'div[data-shortname="'+textValue.substring(0,2)+'"]';
        }

        $('#'+listtype+' .listcont '+div).each(function(){
            if( $(this).attr('data-value').match(inputregex) ){
                var node = $(this).clone();
                $(obj).parent('.'+contlist).children('.dropmenu').append(node);
            }
        });
        if( $(obj).parent('.'+contlist).children('.dropmenu').children('div').length == 0){
            $(obj).parent('.'+contlist).children('.dropmenu').append('<div>Nessun risultato</div>');
        }
        showDropmenu(obj, contlist);
    }else{
        appendDropmenu(obj, contlist, listtype, droptype, true);
    }

    if($(obj).hasClass('postalcode') && $(obj).val() == '') {
        $(obj).parent('div').parent('td').removeClass('valid-1').removeClass('valid-2').addClass('valid-0');
    }
    if($(obj).hasClass('province') && $(obj).val() == '') {
        $(obj).parent('div').parent('td').removeClass('valid-1').removeClass('valid-0').addClass('valid-2');
    }
    if($(obj).hasClass('city') && $(obj).val() == '') {
        $(obj).parent('div').parent('td').removeClass('valid-1').removeClass('valid-0').addClass('valid-2');
    }
    change_content_color($(obj).parents('.tabled').attr('id').replace('tabledata-',''));
    setTimeout(function(){$(obj).focus()},100);
}

function showDropmenu(obj, contlist){
    //open dropmenu triple province-city-postalcode
    var idpage = $('.page.active').attr('id');
    var numarray = idpage.split('-');
    $('.dropmenu.show').removeClass('show');
    $(obj).parent('.'+contlist).children('.dropmenu').addClass('show');

    var listH = $('#page-'+numarray[1]+' .dropmenu.show').height();
    var id = $('#page-'+numarray[1]+' .dropmenu.show').parent('div').attr('id');
    var idArray = id.split('-');

    var table = document.getElementById('tabledata-'+numarray[1]);
    var firstRow = table.rows[1];
    var numFirstRow = parseInt($(firstRow).attr('data-row')) - 1;
    var lastRow = table.rows[ table.rows.length - 1 ];
    var numLastRow = parseInt($(lastRow).attr('data-row')) ;
    var tdH = 39;
    var numCurrentRow = parseInt(idArray[1]) - numFirstRow;
    var currentHeight = numCurrentRow * tdH;
    var totalHeight = ((numLastRow - numFirstRow) * tdH);
    var tocheck = currentHeight + listH ;
    if( tocheck > totalHeight ){
        totalHeight = tocheck + 60;
        $('#page-'+numarray[1]+' .listcontainer').css('height', totalHeight+'px');
    }
    setTimeout(function(){$(obj).focus()},1000);
}


function initializeList(){
    //initialize item of city list
    $('.listcont div').each(function(){
        $(this).attr('data-shortname', $(this).attr('data-value').substring(0,2));
    });
}


function appendDropmenu(obj, contlist, listtype, droptype, isupdate){
    // append dropmenu for the first time in the triple province-city-postalcode
    if(isupdate) $(obj).parent('.'+contlist).children('.dropmenu').remove();

    if( $(obj).parent('.'+contlist).children('.dropmenu').length == 0 || isupdate){
        $(obj).parent('.'+contlist).append('<div class="'+droptype+' dropmenu">'+$('#'+listtype+' .'+droptype).html()+'</div>');
    }

    if( $(obj).val() == '' || isupdate){
        showDropmenu(obj, contlist);
    }else{
        var isprovince = false;
        if( $(obj).hasClass('province') ) isprovince = true;
        updateDropmenu(obj, contlist, listtype, droptype, isprovince);
    }

    $('.'+droptype).on('mouseleave', function(){
        $(this).removeClass('show');
    });
    setTimeout(function(){$(obj).focus()},100);
}

function selectDropItem(obj, contlist, type){
    //call to APi when province city or postalcode is selected
    $('.listcontainer').attr('style', '');
     var data = $(obj).attr("data-value");
     $(obj).parent('.dropmenu').parent('.'+contlist).children('input').val(data);
     var id = $(obj).parent('.dropmenu').parent('.'+contlist).children('input').attr('id');

     if( type == 'province'){
        var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_province?province='+$('#'+id).val();
        checkProvince(id, $(obj).val(), urlrequest, 'province');
     }else if(type=='city'){
        var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_city?city='+$('#'+id).val();
        checkCity(id, $(obj).val(), urlrequest, 'city');
     }else if ( type == 'postalcode'){
        var urlrequest = $('#hidden_ckan_url').text()+'/api/action/validate_postalcode?postalcode='+$('#'+id).val();
        checkPostalcode(id, $(obj).val(), urlrequest, 'postalcode');
     }

     closeDropdown();
}

function closeDropdown(){
    //close dropmenu
    $('.dropmenu').removeClass('show');
}

function deleterow() {
    //open view fro delete rows
    var idpage = $('.page.active').attr('id');
    if($('#tabledata-1 .select-row-del').hasClass('show')){
        $('.tabled').attr('style','');
        $('.select-row-del, .btn-delete').removeClass('show');
    }else{
        var newWidth =  $('.tabled:eq(0)').width() + $('#tabledata-1 .select-row-del').width()+11;
        newWidth = newWidth.toString();
        $('.tabled').css('width', newWidth+'px');
        $('.select-row-del, .btn-delete').addClass('show');
    }
}

function do_delete() {
    //get all row to be deleted
    var idpage = $('.page.active').attr('id');
    if($(".page .tabled input:checked").length > 0) {
        var table_id_list = [];
        $(".page .tabled input:checked").each(function() {
            var num = $(this).attr('data-row');
            var inputs_to_check = $('.page .tabled tr[data-row="'+num+'"] input');
            var all_empty = true;
            for(var i=1; i<inputs_to_check.length; i++) {
                if(inputs_to_check[i].value != '') {
                    all_empty = false;
                }
            }
            if(all_empty == false) {
                table_id_list.push(num);
            } else {
                $(this).parent('td').parent('tr').remove();
            }
        });
        if(table_id_list.length > 0) {
            $('.trash-confirm').addClass('show');
        } else {
            $('.select-row-del').removeClass('show');
            $('.btn-delete').removeClass('show');
        }
    } else {
        $('#alert-row').modal();
    }
}

function confirm_delete(confirm) {
    //delete confirmation
    if(confirm) {
        $(".page .tabled input:checked").each(function() {
            $(this).parent('td').parent('tr').remove();
        });
    }
    $('.select-row-del, .trash-confirm, .btn-delete').removeClass('show');
    $(".page .tabled").attr('style', '');
    for( var i = 1; i<=parseInt($('#hidden_page_number').text()); i++){
        change_content_color(i);
    }
}

function addrow() {
    //add a single row in the last page
    if($('.page').length < parseInt($('#hidden_page_number').text())) {
        return;
    }
    var lastTableId = 'tabledata-'+$('#hidden_page_number').text();
    var latsTable = document.getElementById(lastTableId);
    var lastRow = latsTable.rows[ latsTable.rows.length - 1 ];
    var data_row = $(lastRow).attr('data-row');
    if( data_row === undefined ){
        var num = parseInt($('#hidden_page_number').text()) - 1;
        var secondlastTableId = 'tabledata-'+num;
        var secondlatsTable = document.getElementById(secondlastTableId);
        lastRow = secondlatsTable.rows[ secondlatsTable.rows.length - 1 ];
        data_row = $(lastRow).attr('data-row');
    }
    var inputs_to_check = $('.tabled tr[data-row="'+data_row+'"] input');
    var all_empty = true;
    for(var i=1; i<inputs_to_check.length; i++) {
        if(inputs_to_check[i].value != '') {
            all_empty = false;
        }
    }
    if(all_empty == true) {
        return;
    }
    var show = '';
    if($('#tabledata-1 .select-row-del').hasClass('show')){
        show = 'show';
    }
    var numLastRow = parseInt($(lastRow).attr('data-row')) + 1;
    $('#'+lastTableId+' tbody').append(''
     +'<tr data-row="'+numLastRow+'">'
            +'<td class="valid-0 num-row">'+numLastRow+'</td>'
            +'<td class="valid-0 select-row-del '+show+'"><input type="checkbox" value="" data-row="'+numLastRow+'"></td>'
            +'<td class="valid-0"><input id="othercategoryita-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="othercategoryeng-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-2"><input id="nameita-'+numLastRow+'" class="nameita form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="nameeng-'+numLastRow+'" class="nameeng form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="abbrevita-'+numLastRow+'" class="abbrevita form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="abbreveng-'+numLastRow+'" class="abbreveng form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="descriptionshortita-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="descriptionshorteng-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="descriptionlongita-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="descriptionlongeng-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="phone-'+numLastRow+'" class="phone form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="fax-'+numLastRow+'" class="fax form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="url-'+numLastRow+'" class="url form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="email-'+numLastRow+'" class="email form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="refperson-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-2">'
                +'<div class="contlistprovince" id="contprovince-'+numLastRow+'">'
                    +'<input id="province-'+numLastRow+'" type="text" class="province form-control" value="">'
                +'</div>'
            +'</td>'
            +'<td class="valid-2">'
                +'<div class="contlistcity" id="contcity-'+numLastRow+'">'
                    +'<input id="city-'+numLastRow+'" type="text" class="city form-control" value="">'
                +'</div>'
            +'</td>'
            +'<td class="valid-0">'
                +'<div class="contlistpostalcode" id="contpostalcode-'+numLastRow+'">'
                    +'<input id="postalcode-'+numLastRow+'" type="text" class="postalcode form-control" value="">'
                +'</div>'
            +'</td>'
            +'<td class="valid-0"><input id="streetaddress-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="civicnumber-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="secondphone-'+numLastRow+'" class="secondphone form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="secondfax-'+numLastRow+'" class="secondfax form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="secondemail-'+numLastRow+'" class="secondemail form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="secondstreetaddress-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="secondcivicnumber-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="notes-'+numLastRow+'" class="form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="timetable-'+numLastRow+'" class="form-control " value="" type="text"></td>'
            +'<td class="valid-0"><input id="photo-'+numLastRow+'" class="photo form-control" value="" type="text"></td>'
            +'<td class="valid-2"><input id="lat-'+numLastRow+'" class="latitude form-control" value="" type="text"></td>'
            +'<td class="valid-2"><input id="lon-'+numLastRow+'" class="longitude form-control" value="" type="text"></td>'
            +'<td class="valid-0"><input id="streetId-'+numLastRow+'" class="streetId form-control" value="" type="text"></td>'
    +'</tr>');

    $('.chpage:last').click();
    $('#'+lastTableId+' input').off();
    addListeners('#'+lastTableId);
}

function changeCategory(category){
    //get a list of categories
    var urlbase = $('#hidden_ckan_url').text()+'/api/action/validate_class?Category='+category;
    $.ajax({
        url: urlbase,
        method: 'GET',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        //data: {'Category':category},
        success: function(data, textStatus, jqXHR ) {
            if( data.success == true ){
                filterSubCategory(data.result.cateng_original, data.result.cateng_modified);
            }else{
                showError();
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function changeSubCategory(subcategory){
    // get a list of subcategories
    var urlbase = $('#hidden_ckan_url').text()+'/api/action/validate_categoryEng?cat_name='+subcategory;
        $.ajax({
            url: urlbase,
            method: 'GET',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('Accept', 'application/json');
                xhr.setRequestHeader('Authorization', $('#hidden_key').text());
            },
            //data: {'cat:name':subcategory},
            success: function(data, textStatus, jqXHR ) {
                if( data.success == true ){
                    filterCategory(data.result.class_original, data.result.class_modified);
                }else{
                    showError();
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function filterSubCategory(data, datamodified){
    //filter subcategories
    $('#categoryEng option').remove();

    $('#categoryEng').append('<option value="empty"></option>');
    for(i=0; i<data.length; i++){
        $('#categoryEng').append('<option value="'+data[i]+'">'+datamodified[i]+'</option>'); //+data[i].split('_').join(' ')+
    }
    $('#categoryEng.selectpicker').selectpicker('refresh');
    $('#categoryEng.selectpicker').selectpicker('deselectAll');
    $('#categoryEng.selectpicker').selectpicker('val', 'empty');
}

function filterCategory(data, datamodified){
    //filter category
    $('#category.selectpicker').selectpicker('deselectAll');
    $('#category.selectpicker').selectpicker('val', data);
}

function showError(){
    //show category error
    $('#catError').addClass('active');
    setTimeout(function(){
            $('#catError').removeClass('active');
    },2000);
}

function checkField(idname, parameter, urlrequest, type){
    //check each field with a call to API
    $.ajax({
        url: urlrequest,
        method: 'GET',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        success: function(data, textStatus, jqXHR ) {
            if( data.success == true ){
                $('#'+idname).val(data.result.value);

                if( $('#'+idname).val() == '' &&  type != 'latitude' && type != 'longitude' ){
                    $('#'+idname).parent('td').removeClass('valid-2').addClass('valid-0');
                    $('#inputModalField').removeClass('valid-2');
                    change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''))
                    return;
                }

                if( data.result.valid != 2 ){
                    removeErrorFromTd(idname);
                    removeErrorFromModal('inputModalField');
                }else{
                    addErrorToTd(idname);
                    addErrorToModal('inputModalField');
                }

            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function removeErrorFromTd(idname){
    //remove error from input field
    $('#'+idname).parent('td').removeClass('valid-2');
    $('#'+idname).parent('td').addClass('valid-1');
    change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function addErrorToTd(idname){
    //add error from input field
    $('#'+idname).parent('td').removeClass('valid-0');
    $('#'+idname).parent('td').removeClass('valid-1');
    $('#'+idname).parent('td').addClass('valid-2');
    change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function removeErrorFromModal(idname){
    //remove error from modal
    $('#'+idname).removeClass('valid-2');
    $('#'+idname).addClass('valid-1');
    //change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function addErrorToModal(idname){
    //add error from modal
    $('#'+idname).removeClass('valid-0');
    $('#'+idname).removeClass('valid-1');
    $('#'+idname).addClass('valid-2');
    //change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function removeErrorFromTdRegion(idname, idcity, idpostalcode, found1){
    //remove error to triple province-city-postalcode
    $('#'+idname).parent('div').parent('td').removeClass('valid-2');
    $('#'+idname).parent('div').parent('td').addClass('valid-1');

    $('#'+idcity).parent('div').parent('td').removeClass('valid-2');
    $('#'+idcity).parent('div').parent('td').addClass('valid-1');
    
    if( found1 ){
        $('#'+idpostalcode).parent('div').parent('td').removeClass('valid-2');
        $('#'+idpostalcode).parent('div').parent('td').addClass('valid-1');
    }

    change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function addErrorToTdRegion(idname, idcity, idpostalcode, type, foundprovince, foundpostalcode){
    //add error to triple province-city-postalcode

    if( type != 'province'  &&  $('#'+idname).val() != '' && !foundprovince){
        $('#'+idname).parent('div').parent('td').removeClass('valid-0');
        $('#'+idname).parent('div').parent('td').removeClass('valid-1');
        $('#'+idname).parent('div').parent('td').addClass('valid-2');
        $('#'+idname).val("");
        $('#'+idname).attr('placeholder', 'provincia non corrispondente');
    }

    $('#'+idcity).parent('div').parent('td').removeClass('valid-0');
    $('#'+idcity).parent('div').parent('td').removeClass('valid-1');
    $('#'+idcity).parent('div').parent('td').addClass('valid-2');
    if( type != 'city' &&  $('#'+idcity).val() == '' && !foundprovince){
        $('#'+idcity).val("");
        $('#'+idcity).attr('placeholder', 'città non corrispondente');
        if( $('#'+idname).val() != "" ){
            $('#'+idname).parent('div').parent('td').removeClass('valid-0');
            $('#'+idname).parent('div').parent('td').removeClass('valid-2');
            $('#'+idname).parent('div').parent('td').addClass('valid-1');
        }
    }

    if( !foundpostalcode && type == 'postalcode'){
        $('#'+idpostalcode).parent('div').parent('td').removeClass('valid-0');
        $('#'+idpostalcode).parent('div').parent('td').removeClass('valid-1');
        $('#'+idpostalcode).parent('div').parent('td').addClass('valid-2');
    }
    change_content_color($('#'+idname).parents('.tabled').attr('id').replace('tabledata-',''));
}

function checkElementInArray(list, idcity){
    //check if element exists in array
    var iter = 0;
    var found = false;
    while(!found && iter<list.length){
        if( list[iter] == $('#'+idcity).val()  )found = true;
        iter++;
    }
    return found;
}

function checkSingleValue(value, id){
    //check if value exists in array
    var found = false;
    if( value == $('#'+id).val()) found = true;
    return found;
}

function validateRegion(found, found1, idprovince, idcity, idpostalcode, type){
    //validate triple province-city-postalcode
    if(found && found1) {
        removeErrorFromTdRegion(idprovince, idcity, idpostalcode, found1);
    }else if(found && !found1){
        removeErrorFromTdRegion(idprovince, idcity, idpostalcode, found1);
    }else{
        addErrorToTdRegion(idprovince, idcity, idpostalcode, type, found, found1);
        if( $('#'+idpostalcode).val() != '' && type != 'postalcode'){
             if( !found1 ){
                $('#'+idpostalcode).val("");
                $('#'+idpostalcode).attr('placeholder', 'cap non corrispondente');
                $('#'+idpostalcode).parent('div').parent('td').removeClass('valid-1').removeClass('valid-2').addClass('valid-0');
             }
        }
    }
    if( $('#'+idpostalcode).val() == '' ){
        $('#'+idpostalcode).parent('div').parent('td').removeClass('valid-2');
        change_content_color($('#'+idpostalcode).parents('.tabled').attr('id').replace('tabledata-',''));
    }

}


function checkProvince(idname, parameter, urlrequest, type){
    //check province selected calling API
    $.ajax({
        url: urlrequest,
        method: 'GET',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        success: function(data, textStatus, jqXHR ) {
            if( data.success == true ){
                var number = idname.split('-');
                //change city list
                updateListOfBrother('city', data.result.cities_list, number[1], false);

                //change postalcode list
                updateListOfBrother('postalcode', +data.result.postalcode_list, number[1], false);

                var idcity = 'city-'+number[1];
                var idpostalcode = 'postalcode-'+number[1];
                var found = checkElementInArray(data.result.cities_list, idcity );
                var found1 = checkElementInArray(data.result.postalcode_list, idpostalcode );

                validateRegion(found, found1, idname, idcity, idpostalcode, 'province');

            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function updateListOfBrother(type, list, number, singleValue){
    //update drop list, in a row, for triple province-city-postalcode
    var text = '<div class="dropmenu'+type+' dropmenu">';
    if(singleValue){
        text += '<div data-value="'+list+'" data-shortname="'+list.substring(0,2)+'"'+
             'onclick="selectDropItem(this, \'contlist'+type+'\', \''+type+'\')">'+list+'</div>';
    }else{
        for( i=0; i<list.length; i++){
            text += '<div data-value="'+list[i]+'" data-shortname="'+list[i].substring(0,2)+'"'+
             'onclick="selectDropItem(this, \'contlist'+type+'\', \''+type+'\')">'+list[i]+'</div>';
        }
    }
    text += '</div>';
    $('#cont'+type+'-'+number+' .dropmenu'+type).remove();
    var container = document.getElementById('cont'+type+'-'+number);
    container.insertAdjacentHTML('beforeEnd', text);
}


function checkCity(idname, parameter, urlrequest, type){
    //check city selected calling API
    $.ajax({
        url: urlrequest,
        method: 'GET',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        success: function(data, textStatus, jqXHR ) {
            if(data.success == true) {

                var number = idname.split('-');
                //change province
                updateListOfBrother('province', data.result.province, number[1], true);
                $('#contprovince-'+number[1]+' input').val(data.result.province);
                //change postalcode
                updateListOfBrother('postalcode', data.result.postalcode_list, number[1], false);
                if($('#contpostalcode-'+number[1]).parent('td').hasClass('valid-1')){
                    var capOk = false;
                    for( i=0; i<data.result.postalcode_list.length; i++ ){
                        if( data.result.postalcode_list[i] == $('#contpostalcode-'+number[1]+' input').val() ) capOk = true;
                    }
                    if(!capOk){
                        $('#contpostalcode-'+number[1]+' input').val(data.result.postalcode_list[0])
                    }
                }else{
                    $('#contpostalcode-'+number[1]+' input').val(data.result.postalcode_list[0]);
                }
                var idprovince = 'province-'+number[1];
                var idpostalcode = 'postalcode-'+number[1];
                var found = checkSingleValue(data.result.province, idprovince );
                var found1 = checkElementInArray(data.result.postalcode_list, idpostalcode );

                validateRegion(found, found1, idprovince, idname, idpostalcode, 'city');

            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function checkPostalcode(idname, parameter, urlrequest, type){
    //check postalcode selected calling API
        $.ajax({
            url: urlrequest,
            method: 'GET',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('Accept', 'application/json');
                xhr.setRequestHeader('Authorization', $('#hidden_key').text());
            },
            success: function(data, textStatus, jqXHR ) {
                if( data.success == true ){
                    var number = idname.split('-');
                    var idprovince = 'province-'+number[1];
                    var idcity = 'city-'+number[1];
                    var found = checkSingleValue(data.result.province, idprovince );
                    var found1 = checkSingleValue(data.result.city, idcity );

                    validateRegion(found, found1, idprovince, idcity, idname, 'postalcode');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}

function checkValidate() {
    //check if all information in table and in select are correct
    var can_validate = true;
    var can_validate_subcategory = true;
    if($('#categoryCont').find('span:first').text() == 'Nessuna categoria selezionata') {
        can_validate_subcategory = false;
    }
    if($('#categoryEngCont').find('span:first').text() == 'Nessuna sottocategoria selezionata') {
        can_validate_subcategory = false;
    }
    if(can_validate == true) {
        $('.tabled tbody tr input').each(function () {
            var input_class = $(this).parents('td').attr('class');
            if(input_class !== undefined && input_class.indexOf('valid-2') !== -1) {
                can_validate = false;
            }
        });
    }
    if(can_validate == true && can_validate_subcategory == true) {
        insert_data(false, true);
    } else {
        $('#validatebutton').removeClass('disabled');
        $('#savebutton').removeClass('disabled');
        $('#exportcsv').removeClass('disabled');
        $('#validatebutton').prop("disabled", false);
        $('#savebutton').prop("disabled", false);
        $('#exportcsv').prop("disabled", false);
        var errorLocation = [];

        for(var j=1; j<=$('#hidden_page_number').text(); j++ ){
            $('#tabledata-'+j).each(function(){
                $('#tabledata-'+j+' .valid-2').each(function(){
                    var id, page;
                    if( $(this).children('input').length > 0){
                        id = $(this).children('input').attr('id').split('-');
                    }else{
                        id = $(this).children('div').children('input').attr('id').split('-');
                    }
                    page = $(this).parents('.page').attr('id').split('-');
                    var obj = {'page': page[1], 'row': id[1]};
                    var foundOccurrence = false;
                    for(var i=0; i<errorLocation.length; i++){
                        if( errorLocation[i].page == page[1] && errorLocation[i].row == id[1]) foundOccurrence = true;
                    }
                    if(!foundOccurrence) errorLocation.push(obj);
                });
            });
        }
        var text = '<div id="errorPosition" style="color:darkorange;">';
        if(can_validate_subcategory == false) {
            text += 'Non hai selezionato la <em>Categoria</em> o la <em>Sottocategoria</em><br>';
        }
        if(can_validate == false) {
            text += '<br>Errori:<br>'
            var maxNumber = errorLocation.length;
            if( errorLocation.length > 5) maxNumber = 5;
            for(var i=0; i<maxNumber; i++){
                text += 'Pagina '+errorLocation[i].page+' Riga '+errorLocation[i].row+' <br>';
            }
            if( errorLocation.length > maxNumber ){
                var offset = errorLocation.length - maxNumber;
                text += '<p style="color:grey">altri '+offset+' errori presenti...</p>';
            }
        }
        text += '</div>';
        $('#cant-validate .modal-body #errorPosition').remove();
        $('#cant-validate .modal-body').append(text);
        $('#cant-validate').modal();
    }
}


function insert_data(saveCurrentState, redirect) {
    $('#alert-update').modal();
    //create a obj from tables and calling the API to store this object
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
                }else{
                    obj[keys[i]] = $(this).children('td').eq(i+1).children('input').val();
                }
            }
            records.push(obj);
        });
    }

    var number = $('#hidden_number').text();
    var array = JSON.parse(number);

    var cat_value = $('#category').selectpicker('val');
    var subcat_value = $('#categoryEng').selectpicker('val');
    if(cat_value == 'empty') {
        cat_value = '';
    }
    if(subcat_value == 'empty') {
        subcat_value = '';
    }

    var ckan_url = $('#hidden_ckan_url').text();
    var filename = $('.page-heading').text().toLowerCase();
    var data_to_upoad = {'resource_id': $('#hidden_id').text(), 'category': cat_value, 'subcategory': subcat_value,
                         'package_id': $('#hidden_package_id').text(), 'method': 'insert',
                         'records': records, 'filters' : {'_id': array}, 'saveCurrentState': saveCurrentState,
                         'ckan_url': ckan_url, 'filename': filename};
    var insert_url = ckan_url + '/api/action/upsertdata';

    // shut down other ajax call
    if(redirect) {
        window.stop();
    }

    $.ajax({
        url: insert_url,
        method: 'POST',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        data: JSON.stringify(data_to_upoad),
        success: function(data, textStatus, jqXHR ) {
            if(data.result[0] == 'csv error' || data.result[0] == 'post error' || data.result[0] == 'delete error' ){
                setTimeout(function() {
                       $('#alert-update').modal('hide');
                }, 2000);

                setTimeout(function() {
                       showErrorServer(data.result[0]);
                }, 3000);
            }else{
                if(redirect) {
                    var current_url = window.location.href;
                    var idx_resource = current_url.indexOf('resource');
                    var new_url = current_url.slice(0, idx_resource);
                    $(window).unbind('beforeunload');
                    window.location.replace(new_url);
                } else {
                    changeRecordsNumber(data.result[1]);
                    setTimeout(function() {
                        $('#alert-update').modal('hide');
                    }, 3000);
                }
            }
            $('#validatebutton').removeClass('disabled');
            $('#savebutton').removeClass('disabled');
            $('#exportcsv').removeClass('disabled');
            $('#validatebutton').prop("disabled", false);
            $('#savebutton').prop("disabled", false);
            $('#exportcsv').prop("disabled", false);
        },
        error: function (jqXHR, textStatus, errorThrown) {
               showErrorServer(errorThrown);
        }
    });
}

function showErrorServer(text){
    //show error modal
    $('#savebutton').prop("disabled", false);
    $('#server-error .modal-body').text('');
    $('#server-error .modal-body').append('<div>'+text+'.</div><div>Contatta l\'amministratore di sistema</div>');
    $('#server-error').modal();
}

function get_toponimo(rowNumber) {
    // get toponimo calling API
    var lat = $('#lat-'+rowNumber).val();
    var lon = $('#lon-'+rowNumber).val();

    var data_to_upoad = {'latitude': lat, 'longitude': lon};
    var ckan_url = $('#hidden_ckan_url').text();
    var insert_url = ckan_url + '/api/action/get_toponimo';

    $.ajax({
        url: insert_url,
        method: 'POST',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('Authorization', $('#hidden_key').text());
        },
        data: JSON.stringify(data_to_upoad),
        success: function(data, textStatus, jqXHR ) {
            if(data.result.results.bindings.length > 0) {
                var address = data.result.results.bindings[0].name.value;
                var civic = data.result.results.bindings[0].n.value;
                var urlstreetid = data.result.results.bindings[0].s.value;
                var streetid = urlstreetid.split('/');
                $('#streetId-'+rowNumber).val(streetid[streetid.length-1]);
                if( $('#streetaddress-'+rowNumber).val() == '') $('#streetaddress-'+rowNumber).val(address);
                if( $('#civicnumber-'+rowNumber).val() == '') $('#civicnumber-'+rowNumber).val(civic);
            }
            $('#streetId-'+rowNumber).attr('placeholder', '');
        },
        error: function (jqXHR, textStatus, errorThrown) {
        }
    });
}