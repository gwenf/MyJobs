var readCookie = utils.readCookie;

$(window).ready(function() {
    /*
    Explicit control of main menu, primarily for mobile but also provides
    non hover and cover option if that becomes an issue.
    */
    $(".main-nav").click(function(e){
        e.preventDefault();
        if($(window).width() < 994){
            $("#nav").toggleClass("active");
            // menus
            $(".nav-item").removeClass("no-show");
            // submenus
            $(".sub-nav-item").addClass("no-show");

            $("#back-btn-li").addClass("no-show");

            $(".multiple_companies").addClass("no-show");
            $("#mobile-company-select").addClass("no-show");

            //Not logged in mobile view
            $("#demo-link").removeClass("no-show");
            $("#create-profile").removeClass("no-show");
            $("#login-link").removeClass("no-show");
        }
    });

    $("#pop-menu").mouseleave(function(){
        $("#back-btn-li").addClass("no-show");
        $(".nav-item").removeClass("no-show");
        $(".sub-nav-item").addClass("no-show");

        $("#nav").removeClass("active");
    });

    $(".nav-item").click(function(e) {
      $("#mobile-company-select").removeClass("no-show");
      $("#back-btn-li").removeClass("no-show");
      $(".nav-item").addClass("no-show");
      $(this).nextUntil(".nav-item").removeClass("no-show");
    });

    $("#employers-mobile").click(function(e) {
      $("#company-name-menu").removeClass("no-show");
    });

    $("#back-btn").click(function(e){
        e.preventDefault();

        $(".nav-item").removeClass("no-show");
        $(".sub-nav-item").addClass("no-show");
        $("#back-btn-li").addClass("no-show");
        $("#company-name-menu").addClass("no-show");
    });

    if (typeof tools_companies !== 'undefined') {
        get_companies();
    }
});

function get_companies() {
    // Function builds multiple company elements and functions
    var parent_list_item = document.createElement("li");
    parent_list_item.setAttribute("id", "current-company");
    parent_list_item.setAttribute("class", "submenu-dropdown");

    parent_list_item.onclick = function(event) {
        event.preventDefault();
        var li_last_child = parent_list_item.lastChild;

        if (li_last_child.currentStyle ? li_last_child.currentStyle.display : getComputedStyle(li_last_child, null).display === "none")
            li_last_child.style.display = "block";
        else
            li_last_child.style.display = "none";
    };

    var label = document.createElement("a");

    // Company id from myjobs_company cookie
    var cid = readCookie("myjobs_company");

    var list = document.createElement("ul");
    list.setAttribute("id", "select_company");

    // Company name used to show user what current company is selected
    var menu_company_name;

    var company_not_found = false;

    // Creating li items for "list" (the ul)
    for(var i=0; i<tools_companies.length; i++) {
        var company = tools_companies[i];

        // Get company name from cid, if cid exists
        if (!menu_company_name) {
            if (cid) {
                if (company.id == cid) {
                    menu_company_name = company.name;
                    company_not_found = false;
                } else {
                    company_not_found = true;
                }
            } else {
                set_cookie(tools_companies[0].id, 14);
                menu_company_name = tools_companies[0].name;
            }
        }

        var list_item = document.createElement("li");
        list_item.setAttribute("id", "company_" + String(company.id));
        list_item.setAttribute("style", "cursor: pointer");
        list_item.innerHTML = "<a>"+company.name+"</a>";
        list_item.onclick = function() {
            // this.id Format: company_COMPANYID
            var item_id = this.id.split("_")[1];

            // 14 = 2 weeks
            set_cookie(item_id, 14);

            // replaces text of main li holding company list
            parent_list_item.firstChild.innerHTML = "<b>"+ this.firstChild.innerHTML +"</b>";

            process_reload();
        };
        list.appendChild(list_item);
    }

    if (company_not_found) {
        set_cookie(tools_companies[0].id, 14);
        menu_company_name = tools_companies[0].name;
    }

    label.innerHTML = "<b>"+ menu_company_name +"</b>";
    parent_list_item.appendChild(label);
    parent_list_item.appendChild(list);

    var parent_element = document.getElementById("employer-apps"),
        first_child = parent_element.firstChild;
    parent_element.insertBefore(parent_list_item, first_child);

    // Mobile
    var mobile_parent_element = document.createElement("li"),
        mobile_label = document.createElement("a");
    mobile_parent_element.setAttribute("id", "mobile-company-select");
    mobile_parent_element.setAttribute("class", "no-show");
    mobile_parent_element.setAttribute("style", "cursor:pointer");
    mobile_label.innerHTML = "<b>" + menu_company_name + "</b>";
    if(menu_company_name.length > 20)
        mobile_label.setAttribute("style", "font-size: 21px");
    mobile_parent_element.appendChild(mobile_label);
    mobile_parent_element.onclick = function() {
        $(".multiple_companies").removeClass("no-show");
        $("#back-btn-li").removeClass("no-show");
        $(".nav-item").addClass("no-show");

        $("#mobile-company-select").addClass("no-show");
    };
    var pop_menu = document.getElementById("company-name-menu"),
        search_item = document.getElementById("employers-mobile");
    $(pop_menu).append(mobile_parent_element);

    for(var j=0; j<tools_companies.length; j++) {
        var mobile_list_item = document.createElement("li");
        mobile_list_item.setAttribute("id", "mobilecompany_" + tools_companies[j].id);
        mobile_list_item.setAttribute("class", "no-show sub-nav-item multiple_companies");
        mobile_list_item.setAttribute("style", "cursor:pointer");
        mobile_list_item.innerHTML = "<a>"+ tools_companies[j].name +"</a>";
        mobile_list_item.onclick = function() {
            var mobile_item_id = this.id.split("_")[1];
            set_cookie(mobile_item_id, 14);
            mobile_parent_element.firstChild.innerHTML = "<b>"+ this.firstChild.innerHTML + "</b>";
            process_reload();
        };
        pop_menu.appendChild(mobile_list_item);
    }
}

function process_reload() {
    /*
    Looks at what path the user is currently in.  If the path is showing
    an app that changing company matters redirect the user to a desired
    location instead of causing a 404.
     */
    var path = window.location.pathname,
        // Apps that changing company IDs would be a problem.
        // Despite being removed from navigation, candidates is still in
        // this list to allow changing of company on the now-delisted page.
        app_names = ["candidates", "prm", "posting"],
        new_href = window.location.protocol + "//" + window.location.host,
        app_name,
        i;

    for(i=0; i < app_names.length; i++) {
        app_name = app_names[i];
        if(path.indexOf(app_name) != -1) {
            if(app_name === "candidates") {
                // window.location.href used instead of window.location.replace
                // to simulate a link instead of a redirect.
                window.location.href = new_href + "/candidates/view/";

                // Return false so code doesn't reach location.reload() as it
                // was causing race conditions
                return false
            }
            else if(app_name === "prm") {
                window.location.href = new_href + "/prm/view/";
                return false
            }
            else if(app_name === "posting") {
                window.location.href = new_href + "/posting/admin/";
                return false
            }
        }
    }
    location.reload();
}

function set_cookie(company_id, days) {
    var expires;
    if(days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        expires = "; expires="+date.toGMTString();
    } else
        expires = "";
    document.cookie = "myjobs_company="+company_id+expires+"; path=/";
}

function delete_cookie() {
    set_cookie("", -1);
}
