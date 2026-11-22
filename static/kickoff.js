(function () {
  var input = document.getElementById("brt"), out = document.getElementById("local");
  if (!input || !out) return;
  function update() {
    var p = (input.value || "16:00").split(":");
    // A June 2027 date, so daylight saving rules for the tournament period apply.
    var utc = Date.UTC(2027, 5, 24, Number(p[0]) + 3, Number(p[1]));
    var d = new Date(utc);
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "your time zone";
    var t = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    var day = d.toLocaleDateString([], { weekday: "short" });
    out.textContent = "In " + tz + ": " + t + " (" + day + ", for a match on Thu 24 June)";
  }
  input.addEventListener("input", update);
  update();
})();
