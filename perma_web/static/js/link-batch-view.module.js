var Papa = require('papaparse');
var Spinner = require('spin.js');

var APIModule = require('./helpers/api.module.js');
var FolderTreeModule = require('./folder-tree.module.js');
var ProgressBarHelper = require('./helpers/progress-bar.helper.js');
var HandlebarsHelpers = require('./helpers/handlebars.helpers.js');

var $batch_details, $saved_path, $export_csv;


var render_batch = function(links_in_batch, folder_id) {
    $batch_details.empty();
    let all_finished = true;
    links_in_batch.forEach(function(link) {
        link.progress = (link.step_count / 5) * 100;
        link.local_url = link.guid ? `${window.host}/${link.guid}` : null;
        switch(link.status){
            case "pending":
            case "in_progress":
                link.isProcessing = true;
                all_finished = false;
                break;
            case "completed":
                link.isComplete = true;
                break;
            default:
                link.isError = true;
                link.error_message = APIModule.stripDataStructure(JSON.parse(link.message));
        }
        let template = HandlebarsHelpers.renderTemplate('#batch-link-row', {"link": link});
        $batch_details.append(jQuery.parseHTML(template));
    });
    if (all_finished) {
        let export_data = links_in_batch.map(function(link) {
            let to_export = {
                "url": link.submitted_url
            };
            if (link.status === "completed") {
                to_export["status"] = "success"
                to_export["error_message"] = ""
                to_export["title"] = link.title;
                to_export["perma_link"] = `${window.location.protocol}//${link.local_url}`;
            } else {
                to_export["status"] = "error"
                to_export["error_message"] = link.error_message
                to_export["title"] = ""
                to_export["perma_link"] = ""
            }
            return to_export;
        });
        let csv = Papa.unparse(export_data);
        $export_csv.attr("href", "data:text/csv;charset=utf-8," + encodeURI(csv));
        $export_csv.attr("download", "perma.csv");
        $export_csv.show();
    }
};

var get_batch_info = function(batch_id) {
    return APIModule.request('GET', '/archives/batches/' + parseInt(batch_id))
        .then(function(batch_data) {
            if (Array.isArray(batch_data.capture_jobs)) {
                return batch_data.capture_jobs
            }
            return [];
        });
};

export function show_batch(batch_id, folder_id) {
    var folder_path = FolderTreeModule.getPathForId(folder_id);
    $saved_path.html(folder_path.join(" &gt; "));
    var spinner = new Spinner({lines: 15, length: 10, width: 2, radius: 9, corners: 0, color: '#222222', trail: 50, top: '20px'}).spin($batch_details[0]);
    var interval = setInterval(function() {
        get_batch_info(batch_id).then(function(links_in_batch) {
            render_batch(links_in_batch, folder_id);
            var all_completed = true;
            for (var i = 0; i < links_in_batch.length; i++) {
                var link = links_in_batch[i];
                if ((link.status === "pending") || (link.status === "in_progress")) {
                    all_completed = false;
                    break;
                }
            }
            if (all_completed) {
                clearInterval(interval);
            }
        });
    }, 2000);
}

export function init() {
    $(function() {
        $batch_details = $('#batch-details');
        $saved_path = $('#batch-saved-path');
        $export_csv = $('#export-csv');
    });
}
