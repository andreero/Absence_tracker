function getURLYearMonth() {
    const pathname = window.location.pathname;
    const defaultDate = new Date()
    let year = new Date().getFullYear();
    let month = null;

    matches = pathname.match('\/(?<year>[1-2][0-9][0-9]{2})\/(?<month>[0-1]?[0-9])?\/?');
    if (matches && matches.length) {
        if (matches.groups.year) {
            year = parseInt(matches.groups.year)
        }
        if (matches.groups.month != null) {
            month = parseInt(matches.groups.month)-1  // Since JS months are 0-based
        }
    }
    return [year, month]
}


function getDaysInYear(year) {
    return ((year % 4 === 0 && year % 100 > 0) || year % 400 == 0) ? 366 : 365;
}

function getDaysInMonth(year, month) {
  return new Date(year, month+1, 0).getDate();
}


function createChart(e) {
    const chartWidth = document.querySelector('.chart-columns').offsetWidth;
    const chartLeft = document.querySelector('.chart-columns').offsetLeft;
    const tasks = document.querySelectorAll('a.chart-bar');

    const [urlYear, urlMonth] = getURLYearMonth();
    const monthlyView = (urlMonth != null);
    let calendarLength = getDaysInYear(urlYear);

    if (monthlyView){
        calendarLength = getDaysInMonth(urlYear, urlMonth);
    }

    tasks.forEach(el => {
        const startDay = el.dataset.absenceStart;
        const endDay = el.dataset.absenceEnd;

        const startDate = new Date(startDay+'Z');
        const endDate = new Date(endDay+'Z');
        let startShare = 0;
        let endShare = calendarLength;

        if (monthlyView){
            startShare = Math.floor((startDate.getTime() - new Date(urlYear, urlMonth, 0).getTime()) / 86400000) - 1;
            endShare = Math.floor((endDate.getTime() - new Date(urlYear, urlMonth, 0).getTime()) / 86400000);
        } else {
            startShare = Math.floor((startDate.getTime() - new Date(urlYear, 0, 0).getTime()) / 86400000) - 1;
            endShare = Math.floor((endDate.getTime() - new Date(urlYear, 0, 0).getTime()) / 86400000);
        }
        console.log(monthlyView, calendarLength, startShare, endShare, urlYear, urlMonth)
        console.log(new Date(urlYear, urlMonth, 0))


        if (startShare < 0) {
            startShare = 0;
        } else if (startShare > calendarLength) {
            startShare = calendarLength;
        }

        if (endShare < 0) {
            endShare = 0;
        } else if (endShare > calendarLength) {
            endShare = calendarLength;
        }
        console.log(monthlyView, calendarLength, startShare, endShare, urlYear, urlMonth)

        let left = chartLeft + Math.floor(chartWidth*startShare/calendarLength);
//        let width = Math.ceil(chartWidth*(endShare-startShare)/calendarLength);
        let width = chartLeft + Math.ceil(chartWidth*endShare/calendarLength) - left;

        // apply css
        el.style.left = left+'px';
        el.style.width = width+'px';
        if (e.type == "load") {
            el.style.position = 'absolute';
            el.style.display = 'inline-block';
            el.style.opacity = 1;

            switch (el.dataset.approvalStatusCode) {
                case '0':
                    el.style.backgroundColor = "#d1d5db"; break; //grey
                case '1':
                    el.style.backgroundColor = "#ea580c"; break; //orange
                case '2':
                    el.style.backgroundColor = "#15803d"; break;  //green
                case '3':
                    el.style.backgroundColor = "#b91c1c"; break;  //red
                default:
                    el.style.backgroundColor = "#1d4ed8"; break;  //blue
            }
        }
  });
}

window.addEventListener("load", createChart);
window.addEventListener("resize", createChart);