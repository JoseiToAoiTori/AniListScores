const fs = require('fs');
const fetch = require('node-fetch');

const regexData = [];
const jsonData = {
	MediaListCollection: {
		lists: [{
			name: "Completed",
			isCustomList:false,
			isSplitCompletedList:false,
			entries: [],
		}],
	},
	User: {
		name: "NAME_HERE",
		id: 518490,
		mediaListOptions: {
			scoreFormat: "POINT_10_DECIMAL",
		},
	},
	version:"1.01",
   	scriptInfo: {
    	version:"9.76",
    	name:"Automail",
    	link:"https://greasyfork.org/en/scripts/370473-automail",
    	repo:"https://github.com/hohMiyazawa/Automail",
    	firefox:"https://addons.mozilla.org/en-US/firefox/addon/automail/",
    	chrome:"NO KNOWN BUILDS",
    	author:"hoh",
    	authorLink:"https://anilist.co/user/hoh/",
    	license:"GPLv3"
	},
   type:"ANIME",
   url:"https://anilist.co/settings/import",
   timeStamp:1591006822628,
};
let anilistData = [];
const showQuerySimple = `query ($id: [Int], $page: Int, $perPage: Int) {
	Page(page: $page, perPage: $perPage) {
	  pageInfo {
		total
		currentPage
		lastPage
		hasNextPage
	  }
	  results: media(type: ANIME, id_in: $id) {
		id
		format
		episodes
		idMal
		startDate {
		  year
		}
		title {
		  romaji
		  english
		  native
		}
		coverImage {
		  large
		  extraLarge
		}
		siteUrl
	  }
	}
  }
  `;
const regex = /[0-9]*,\d*\.?\d*,\d*\.?\d*,\d*\.?\d*,\d*\.?\d*,\d*\.?\d*/mg;

async function readData () {
	fs.readFile('./scores.csv', async (err, data) => {
		if (err) throw err;
		while ((m = regex.exec(data)) !== null) {
			// This is necessary to avoid infinite loops with zero-width matches
			if (m.index === regex.lastIndex) {
				regex.lastIndex++;
			}
			// The result can be accessed through the `m`-variable.
			m.forEach(match => {
				const arr = match.split(',');
				regexData.push({
					id: arr[0],
					uw_avg: arr[1],
					w_avg: arr[2],
					users: arr[3],
					w_dev: arr[4],
					uw_dev: arr[5],
				});
			});
		}
		fetchData();
	});
}

async function fetchData () {
	let page = 1;
	let hasNext = true;
	while (hasNext) {
			const response = await fetch('https://graphql.anilist.co', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Accept': 'application/json',
				},
				body: JSON.stringify({
					query: showQuerySimple,
					variables: {
						id: regexData.map(element => element.id),
						page,
						perPage: 50,
					},
				}),
			});
			if (!response.ok) return alert('no bueno');
			const data = await response.json();
			anilistData = [...anilistData, ...data.data.Page.results];
			hasNext = data.data.Page.pageInfo.hasNextPage;
			console.log(`Fetched page ${page}`);
			page++;
	}
	generateJSON();
	outputFile();
}

function generateJSON () {
	let rank = 1;
	for (const anime of regexData) {
		const found = anilistData.find(element => element.id == anime.id);
		jsonData.MediaListCollection.lists[0].entries.push({
			mediaId: found.id,
			status: "COMPLETED",
			progress: found.episodes,
			repeat: parseInt(anime.users),
			notes: `Rank: #${rank}
Completed by: ${anime.users}
Unweighed Avg: ${anime.uw_avg}
Weighed Dev: ${anime.w_dev}
Unweighed Dev: ${anime.uw_dev}`,
			priority: 0,
			hiddenFromStatusLists:false,
			customLists:null,
			advancedScores:{
				Story:0,
				Characters:0,
				Visuals:0,
				Audio:0,
				enjoyment:0
			},
			startedAt:{
				year:2020,
				month:7,
				day:1,
			},
			completedAt:{
				year:2019,
				month:7,
				day:1,
			},
			media: {
				idMal: found.idMal,
				title: found.title,
			},
			score: Math.round(anime.w_avg * 10) / 10,
		});
		rank++;
	}
}

function outputFile () {
	fs.writeFile('AnimeList.json', JSON.stringify(jsonData), (err) => {
		if (err) throw err;
	});
}

readData();
