$(document).ready(function(){
    $.fn.datepicker.defaults.language = 'it';
    $.fn.datepicker.defaults.format = 'dd/mm/yyyy';
    $("#from_date").datepicker({
        autoclose: true,
        todayHighlight: true,
        startDate: 'd',
        minDate: '+2y'
    }).on('changeDate', function(selectedDate){
        var startDate = new Date(selectedDate.date.valueOf());
        $('#until_date').datepicker('setStartDate', startDate);
    });

    $("#until_date").datepicker({
        autoclose: true,
        todayHighlight: true,
        startDate: 'd',
        endDate: '+2y'
    }).on('changeDate', function(selectedDate){
        var endDate = new Date(selectedDate.date.valueOf());
        $('#from_date').datepicker('setEndDate', endDate);
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