function tab(tabName) {
        document.getElementById('InfoTabContent').style.display = 'none';
        document.getElementById('TreeTabContent').style.display = 'none';
        document.getElementById('StatsTabContent').style.display = 'none';
        document.getElementById('DiscTabContent').style.display = 'none';
        document.getElementById('InfoTab').setAttribute("class", "");
        document.getElementById('TreeTab').setAttribute("class", "");
        document.getElementById('StatsTab').setAttribute("class", "");
        document.getElementById('DiscTab').setAttribute("class", "");
        document.getElementById(tabName+'Content').style.display = 'block';
        document.getElementById(tabName).setAttribute("class", "active");
}