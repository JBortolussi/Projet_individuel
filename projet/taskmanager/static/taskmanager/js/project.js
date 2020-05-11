filter_button = document.getElementById("filter_button");
row_filter = document.getElementById("row-filter");
// row_table =  document.getElementById("row-table");
filter_div = document.getElementById("filter-div");

let filter_on = new Boolean(false);
let input_number = 0;

function filter_button_function(){
    row_filter.classList.toggle('unactive');
}
filter_button.onclick = filter_button_function;

function remove_input(id) {
    // let input = document.getElementById("filter-sel-" + id);
    // let text = document.getElementById("filter-txt-" + id);
    // let button = document.getElementById("filter-del-" + id);
    // let br = document.getElementById("filter-br-" + id);
    //
    // let parent = input.parentNode;
    // parent.removeChild(input);
    // parent.removeChild(text);
    // parent.removeChild(button);
    // parent.removeChild(br);

    let row = document.getElementById("filter-row-" + id);
    let parent = row.parentNode;
    parent.removeChild(row);
}

function new_select_filter(id) {
    let input = document.createElement("SELECT");
    input.setAttribute('id', "filter-sel-" + id);
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
    select.setAttribute('id', 'filter-link-' + id);

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
function add_input(text_value="", select_value="assign") {
    input_number += 1;

    let select = new_select_filter(input_number);
    select.value = select_value;
    select.setAttribute('name', input_number);

    let link = new_select_link(input_number);
    link.setAttribute('name', input_number);

    // text possiblity
    let text_text = document.createElement("INPUT");
    text_text.setAttribute('type', 'text');
    text_text.setAttribute('name', input_number);
    text_text.setAttribute('class', 'form-control');
    text_text.value = text_value;

    let text_user = document.createElement("SELECT");
    text_user.setAttribute('name', input_number);
    text_user.setAttribute('class', 'form-control');
    for (let i = 0; i < user_tab.length; i++){
        let opt = document.createElement("OPTION");
        opt.setAttribute('value', user_tab[i][1]);
        opt.appendChild(document.createTextNode(user_tab[i][0]));
        text_user.appendChild(opt);
    }
    text_user.value = text_value;

    let text_status = document.createElement("SELECT");
    text_status.setAttribute('name', input_number);
    text_status.setAttribute('class', 'form-control');
    for (let i = 0; i < status_tab.length; i++){
        let opt = document.createElement("OPTION");
        opt.setAttribute('value', status_tab[i][1]);
        opt.appendChild(document.createTextNode(status_tab[i][0]));
        text_status.appendChild(opt);
    }
    text_status.value = text_value;

    let text_date = document.createElement("INPUT");
    text_date.setAttribute('name', input_number);
    text_date.setAttribute('type', 'date');
    text_date.setAttribute('class', 'form-control');
    text_date.value = text_value;

    text_dic['' + input_number] = [text_text, text_user, text_status, text_date];

    select.addEventListener("change",function() {
        id = this.name;
        col2 = document.getElementById("col2-" + id);
        child = col2.firstChild;
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
    // del.setAttribute('type', "button");
    // del.setAttribute('value', 'remove');
    del.setAttribute('onclick', "remove_input(" + input_number + ")");

    let col1 = document.createElement('DIV');
    col1.setAttribute('class', 'col-sm-3');
    col1.appendChild(select);

    let col2 = document.createElement('DIV');
    col2.setAttribute('id', 'col2-' + input_number);
    col2.setAttribute('class', 'col-sm-3');
    col2.appendChild(text_dic['' + input_number][1]);

    let col3 = document.createElement('DIV');
    col3.setAttribute('class', 'col-sm-2');
    col3.appendChild(link);

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

    filter_div.appendChild(row);
}


//remplissage du filter-form

add_input();


