console.log("main js working......");

// API endsponits

var scrapeAPI = "/scrape";
var resultAPI = "/result";

// scrape button
var scrape = document.getElementById("scrape");
// geting table object
var tabelData = document.getElementById("table-data");
var toCsv = document.getElementById("toCsv");

// on clicking scraping buttion this fuction scrape links and save html to our local storage
scrape.addEventListener("click", function () {
  console.log("scrape clicked....");
  // values from our form
  var scrape_url = document.getElementById("scrape_url").value;
  var start_page_no = document.getElementById("spn").value;

  var end_page_no = document.getElementById("epn").value;

  var keyword = document.getElementById("keyword").value;

  var locations = document.getElementById("locations").value;
  // checks for form values and value needed befor starting for scraping
  if (scrape_url == "") {
    alert("Please Enter Page URL");
    return;
  }

  if (Number(end_page_no) < Number(start_page_no)) {
    alert("End page number 'should be greater' then start page number");
    return;
  }

  if (Number(end_page_no) - Number(start_page_no) > 35) {
    alert(
      "Diffrence Between End page No and Start Page number should not be greater then 35"
    );
    return;
  }

  // Feedback to enduser that scraping starts
  scrape.style.background = "red";
  scrape.innerText =
    "Scraping starts..... please wait for while to see results!";
  scrape.style.pointerEvents = "none";

  ScrapeAPIFunction(scrape_url, start_page_no, end_page_no, keyword, locations);

  //Show results into table
  // ShowResults(locations, keyword);
});

async function ScrapeAPIFunction(
  scrape_url,
  start_page_no,
  end_page_no,
  keyword,
  locations
) {
  // start scrapeing and saving html pages
  // Fetch API for calling async calls to API
  let scrapeLinksResponse = await fetch(scrapeAPI, {
    method: "POST",
    headers: { "Content-Type": "application/Json" },
    body: JSON.stringify({
      scrape_url: scrape_url,
      start_page_no: start_page_no,
      end_page_no: end_page_no,
      keyword: keyword,
      location: locations,
    }),
  });
  // getting response data
  var responseText = await scrapeLinksResponse.text();
  var arrLinks = await JSON.parse(responseText);
  totalLinks = arrLinks["total_links"];
  if (totalLinks > 1500) {
    alert("Please lower your 'End Page No' ");
    scrape.style.pointerEvents = "auto";
    scrape.style.background = "#007bff";
    scrape.innerText = "Scrape";
  } else {
    scrape.style.background = "green";
    scrape.innerText = "Scraping Completes";
    // this is show the results data
    ShowResults(locations, keyword);
  }
  console.log("Total Links:", totalLinks);

  //END Scrape API
}

async function ShowResults(locations, keyword) {
  for (let idx = 0; idx < 1500; idx += 1) {
    let resultResponse = await fetch(resultAPI, {
      method: "POST",
      headers: { "Content-Type": "application/Json" },
      body: JSON.stringify({
        idx: idx,
        location: locations,
        keyword: keyword,
      }),
    });
    // Fethig data and append into table
    var resultResponseText = await resultResponse.text();
    var resultArr = await JSON.parse(resultResponseText);
    if (resultArr["stop"] === true) {
      console.log("stop fetching....");
      break;
    }
    var row = tabelData.insertRow(idx + 1);
    for (let c = 0; c <= 9; c += 1) {
      var cell = row.insertCell(c);
      cell.innerHTML = resultArr[c];
    }
  }
}

toCsv.addEventListener("click", function () {
  saveTableDataToCookie();
  toCsv.setAttribute("href", "/tocsv");
});
