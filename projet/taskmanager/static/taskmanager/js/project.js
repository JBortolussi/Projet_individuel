filter_button = document.getElementById("filter_button");
row_filter = document.getElementById("row-filter");
// row_table =  document.getElementById("row-table");
filter_div = document.getElementById("filter-div");

let filter_on = new Boolean(false);
let input_number = 0;

function remove_input(id) {
    let row = document.getElementById("filter-row-" + id);
    $("#filter-del-" + id).tooltip('dispose');
    let parent = row.parentNode;
    parent.removeChild(row);
}

function new_select_filter(id) {
    let input = document.createElement("SELECT");
    input.setAttribute('class', 'form-control');

    let assign = document.createElement("OPTION");
    assign.setAttribute('value', 'assign');
    assign.appendChild(document.createTextNode('Assign to'));
    input.appendChild(assign);

    let not_assign = document.createElement("OPTION");
    not_assign.setAttribute('value', 'not_assign');
    not_assign.appendChild(document.createTextNode('Not assign to'));
    input.appendChild(not_assign);

    let status = document.createElement("OPTION");
    status.setAttribute('value', 'status');
    status.appendChild(document.createTextNode('Status :'));
    input.appendChild(status);

    let not_status = document.createElement("OPTION");
    not_status.setAttribute('value', 'not_status');
    not_status.appendChild(document.createTextNode('Not status :'));
    input.appendChild(not_status);

    let start_before = document.createElement("OPTION");
    start_before.setAttribute('value', 'start_before');
    start_before.appendChild(document.createTextNode('To be started before :'));
    input.appendChild(start_before);

    let start_after = document.createElement("OPTION");
    start_after.setAttribute('value', 'start_after');
    start_after.appendChild(document.createTextNode('To be started after :'));
    input.appendChild(start_after);

    let end_before = document.createElement("OPTION");
    end_before.setAttribute('value', 'end_before');
    end_before.appendChild(document.createTextNode('To be ended before :'));
    input.appendChild(end_before);

    let end_after = document.createElement("OPTION");
    end_after.setAttribute('value', 'end_after');
    end_after.appendChild(document.createTextNode('To be ended after :'));
    input.appendChild(end_after);

    return input;
}

function new_select_link(id) {
    let select = document.createElement('SELECt');
    select.setAttribute('class', 'form-control');

    let and = document.createElement('OPTION');
    and.setAttribute('value', 'and');
    and.appendChild(document.createTextNode('AND'));
    select.appendChild(and);

    let or = document.createElement('OPTION');
    or.setAttribute('value', 'or');
    or.appendChild(document.createTextNode('OR'));
    select.appendChild(or);

    return select;
}

let text_dic = {};
function add_input(id=-1) {
    input_number += 1;

    if (id == -1){
        div = filter_div;
    } else {
        div = document.getElementById('div-input-' + id);
    }

    let select = new_select_filter(input_number);
    select.setAttribute('name', input_number);

    let link = new_select_link(input_number);
    link.setAttribute('name', input_number);

    // text possiblity
    let text_text = document.createElement("INPUT");
    text_text.setAttribute('type', 'text');
    text_text.setAttribute('name', input_number);
    text_text.setAttribute('class', 'form-control');

    let text_user = document.createElement("SELECT");
    text_user.setAttribute('name', input_number);
    text_user.setAttribute('class', 'form-control');
    for (let i = 0; i < user_tab.length; i++){
        let opt = document.createElement("OPTION");
        opt.setAttribute('value', user_tab[i][1]);
        opt.appendChild(document.createTextNode(user_tab[i][0]));
        text_user.appendChild(opt);
    }

    let text_status = document.createElement("SELECT");
    text_status.setAttribute('name', input_number);
    text_status.setAttribute('class', 'form-control');
    for (let i = 0; i < status_tab.length; i++){
        let opt = document.createElement("OPTION");
        opt.setAttribute('value', status_tab[i][1]);
        opt.appendChild(document.createTextNode(status_tab[i][0]));
        text_status.appendChild(opt);
    }

    let text_date = document.createElement("INPUT");
    text_date.setAttribute('name', input_number);
    text_date.setAttribute('type', 'date');
    text_date.setAttribute('class', 'form-control');

    text_dic['' + input_number] = [text_text, text_user, text_status, text_date];

    select.addEventListener("change",function() {
        let id = this.name;
        col2 = document.getElementById("col3-" + id);
        let child = col2.firstChild;
        col2.removeChild(child);

        if (this.value == "assign" || this.value == "not_assign"){
            col2.appendChild(text_dic[''+id][1]);
        } else if (this.value == "status" || this.value == "not_status"){
            col2.appendChild(text_dic[''+id][2]);
        } else  if (this.value == "start_after" || this.value == "start_before" || this.value == "end_before" || this.value == "end_after"){
            col2.appendChild(text_dic[''+id][3]);
        }
    });

    let del = document.createElement("I");
    del.setAttribute('id', "filter-del-" + input_number);
    del.setAttribute('data-toggle', 'tooltip');
    del.setAttribute('data-placement', 'right');
    del.setAttribute('title', 'Remove filter');
    del.setAttribute('class', "fas fa-times fa-2x");
    del.style.color = 'tomato';
    del.setAttribute('onclick', "remove_input(" + input_number + ")");

    let col2 = document.createElement('DIV');
    col2.setAttribute('class', 'col-sm-3');
    col2.appendChild(select);

    let col3 = document.createElement('DIV');
    col3.setAttribute('id', 'col3-' + input_number);
    col3.setAttribute('class', 'col-sm-3');
    col3.appendChild(text_dic['' + input_number][1]);

    let col1 = document.createElement('DIV');
    col1.setAttribute('class', 'col-sm-2');
    col1.appendChild(link);

    let col4 = document.createElement('DIV');
    col4.setAttribute('class', 'col-sm-3');
    col4.appendChild(del);

    let row = document.createElement('DIV');
    row.setAttribute('id', 'filter-row-' + input_number);
    row.setAttribute('class', 'row');
    row.appendChild(document.createElement("BR"));
    row.appendChild(document.createElement("BR"));
    row.appendChild(col1);
    row.appendChild(col2);
    row.appendChild(col3);
    row.appendChild(col4);

    div.appendChild(row);
    $("#filter-del-" + input_number).tooltip();
}

function remove_OR_AND(method, id) {
    let row = document.getElementById("filter-row-" + id);
    $("#filter-del-" + id).tooltip('dispose');
    let parent = row.parentNode;

    let div = document.getElementById("div-input-" + id);
    let hr = document.getElementById("hr-" + id);
    let end_or = document.getElementById('input_end_' + method + '-' + id);

    parent.removeChild(row);
    parent.removeChild(div);
    parent.removeChild(end_or);
    parent.removeChild(hr);
}

function add_OR_AND(id=-1, method) {
    input_number += 1;

    if (id == -1){
        div = filter_div;
    } else {
        div = document.getElementById('div-input-' + id);
    }

    let del = document.createElement("I");
    del.setAttribute('id', "filter-del-" + input_number);
    del.setAttribute('data-toggle', 'tooltip');
    del.setAttribute('data-placement', 'right');
    del.setAttribute('title', 'Remove filter');
    del.setAttribute('class', "fas fa-times fa-2x");
    del.style.color = 'tomato';
    del.setAttribute('onclick', "remove_OR_AND(" + '\'' + method + '\'' + ',' + input_number + ")");

    let add = document.createElement("I");
    add.setAttribute('id', "filter-del-" + input_number);
    add.setAttribute('data-toggle', 'tooltip');
    add.setAttribute('data-placement', 'right');
    add.setAttribute('title', 'Add filter');
    add.setAttribute('class', "fas fa-plus fa-2x");
    add.style.marginLeft = "10px"
    add.style.color = 'green';
    add.setAttribute('onclick', "add_input(" + input_number + ")");

    let or =document.createElement("INPUT");
    or.setAttribute('type', 'button');
    or.setAttribute('class', 'btn btn-primary');
    or.setAttribute('value', 'OR');
    or.style.marginLeft = "10px";
    or.setAttribute('onclick', "add_OR_AND(" + input_number + ", \'or\' )");

    let and =document.createElement("INPUT");
    and.setAttribute('type', 'button');
    and.setAttribute('class', 'btn btn-primary');
    and.setAttribute('value', 'AND');
    and.style.marginLeft = "10px";
    and.setAttribute('onclick', "add_OR_AND(" + input_number + ", \'and\' )");

    let input = document.createElement("INPUT");
    input.setAttribute('id', 'input_' + method + '-' + input_number);
    input.setAttribute('name', 'input_' + method + '-' + input_number);
    input.style.display = 'none';

    let input_end = document.createElement("INPUT");
    input_end.setAttribute('id', 'input_end_' + method + '-' + input_number);
    input_end.setAttribute('name', 'input_end_' + method + '-' + input_number);
    input_end.style.display = 'none';

    let row = document.createElement('DIV');
    row.setAttribute('id', 'filter-row-' + input_number);
    row.setAttribute('class', 'row');

    let col_l = document.createElement("DIV");
    col_l.setAttribute('class', 'col-sm-3');
    col_l.innerHTML = "<hr color='grey'>";

    let col_m = document.createElement('DIV');
    col_m.setAttribute('class', 'col-sm-2');
    col_m.style.textAlign = "center";
    col_m.innerHTML = method.toUpperCase();

    let col_r = document.createElement("DIV");
    col_r.setAttribute('class', 'col-sm-3');
    col_r.innerHTML = "<hr color='grey'>";

    let col_del = document.createElement("DIV");
    col_del.setAttribute('class', 'col-sm-3');
    col_del.appendChild(del);
    col_del.appendChild(add);
    col_del.appendChild(or);
    col_del.appendChild(and);

    let div_input = document.createElement("DIV");
    div_input.setAttribute('id', "div-input-" + input_number);


    let hr = document.createElement("DIV");
    hr.innerHTML = "<hr color='grey'>";
    hr.setAttribute('id', 'hr-' + input_number);

    row.appendChild(input);
    row.appendChild(col_l);
    row.appendChild(col_m);
    row.appendChild(col_r);
    row.appendChild(col_del);

    div.appendChild(row);
    $(document).ready(function () {
        $('[data-toggle="tooltip"]').tooltip({
    trigger : 'hover'
    });
    });
    div.appendChild(div_input);
    div.appendChild(input_end);
    div.appendChild(hr);
    add_input(input_number);
}
//remplissage du filter-form
add_input();


