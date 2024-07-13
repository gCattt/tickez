$(document).ready(function(){
    $.fn.datepicker.defaults.language = 'it';
    $.fn.datepicker.defaults.format = 'yyyy-mm-dd';
    $("#from_date").datepicker({
        autoclose: true,
        todayHighlight: true,
        startDate: 'd',
        minDate: '+2y',
        todayBtn: "linked",
    }).on('changeDate', function(selectedDate){
        var startDate = new Date(selectedDate.date.valueOf());
        $('#until_date').datepicker('setStartDate', startDate);
        $('#filterForm').submit();
    });

    $("#until_date").datepicker({
        autoclose: true,
        todayHighlight: true,
        startDate: 'd',
        endDate: '+2y',
        todayBtn: "linked",
    }).on('changeDate', function(selectedDate){
        var endDate = new Date(selectedDate.date.valueOf());
        $('#from_date').datepicker('setEndDate', endDate);
        $('#filterForm').submit();
    });

    var fromDate = $('#from_date').val();
    var untilDate = $('#until_date').val();
    if (fromDate) {
        $('#until_date').datepicker('setStartDate', new Date(fromDate.split('/').reverse().join('/')));
    }
    if (untilDate) {
        $('#from_date').datepicker('setEndDate', new Date(untilDate.split('/').reverse().join('/')));
    }
});