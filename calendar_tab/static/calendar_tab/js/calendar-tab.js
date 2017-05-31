(function ($) {
  $(document).ready(function () {

    scheduler.config.show_loading = true;
    scheduler.init('scheduler_here', new Date(), "month");
    scheduler.load("events/", "json");

    function block_readonly(id) {
      if (!id) return true;
      return !this.getEvent(id).readonly;
    }

    scheduler.attachEvent("onBeforeDrag", block_readonly);
    scheduler.attachEvent("onClick", block_readonly);


    var dp = new dataProcessor("dataprocessor/");
    dp.init(scheduler);
    dp.setTransactionMode("POST", false);
  });
})(jQuery);
