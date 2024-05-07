var res = fetch("https://studio.youtube.com/youtubei/v1/analytics_data/join?alt=json&key=AIzaSyBUPetSUmoZL-OhlxA7wSac5XinrygCqMo", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "SAPISIDHASH 1704015694_6cd589c9a1fb8664b725368b5973038871483676",
    "content-type": "application/json",
    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
    "sec-ch-ua-arch": "\"arm\"",
    "sec-ch-ua-bitness": "\"64\"",
    "sec-ch-ua-full-version": "\"120.0.6099.129\"",
    "sec-ch-ua-full-version-list": "\"Not_A Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"120.0.6099.129\", \"Google Chrome\";v=\"120.0.6099.129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "\"\"",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-ch-ua-platform-version": "\"14.2.1\"",
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-client-data": "CKS1yQEIi7bJAQijtskBCKmdygEI7NzKAQiSocsBCIagzQEI3L3NAQiO4c0BCMjpzQEI3uvNAQi/7s0BCN/uzQEIg/DNARj2yc0BGKfqzQEY642lFw==",
    "x-goog-authuser": "0",
    "x-goog-pageid": "108940515231048981095",
    "x-goog-visitor-id": "CgtkZFlvbGNoZUZUTSjN7sSsBjIKCgJVUxIEGgAgKg%3D%3D",
    "x-origin": "https://studio.youtube.com",
    "x-youtube-ad-signals": "dt=1704015694134&flash=0&frm&u_tz=-300&u_his=50&u_h=956&u_w=1470&u_ah=919&u_aw=1470&u_cd=30&bc=31&bih=353&biw=1470&brdim=0%2C37%2C0%2C37%2C1470%2C37%2C1470%2C919%2C1470%2C353&vis=1&wgl=true&ca_type=image",
    "x-youtube-client-name": "62",
    "x-youtube-client-version": "1.20231219.01.00",
    "x-youtube-delegation-context": "EhhVQ0hQb05Ia19hQzVMbUpERFZBSDR3N1EqAggI",
    "x-youtube-page-cl": "592271021",
    "x-youtube-page-label": "youtube.studio.web_20231219_01_RC00",
    "x-youtube-time-zone": "America/New_York",
    "x-youtube-utc-offset": "-300"
  },
  "referrer": "https://studio.youtube.com/video/x6mcua0HOJs/analytics/tab-reach_viewers/period-default/explore?entity_type=VIDEO&entity_id=x6mcua0HOJs&time_period=since_publish&explore_type=TABLE_AND_CHART&metrics_computation_type=DELTA&metric=VIDEO_THUMBNAIL_IMPRESSIONS&granularity=DAY&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&t_metrics=VIEWS&t_metrics=WATCH_TIME&t_metrics=ESTIMATED_UNIQUE_VIEWERS&v_metrics=VIDEO_THUMBNAIL_IMPRESSIONS&v_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&v_metrics=VIEWS&v_metrics=WATCH_TIME&v_metrics=ESTIMATED_UNIQUE_VIEWERS&dimension=VIDEO&o_column=VIDEO_THUMBNAIL_IMPRESSIONS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "{\"nodes\":[{\"key\":\"0__SINCE_PUBLISH_NON_NORMALIZED_TOTALS_QUERY\",\"value\":{\"query\":{\"dimensions\":[],\"metrics\":[{\"type\":\"ESTIMATED_UNIQUE_VIEWERS\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20231226,\"exclusiveEnd\":20240101}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"0__SINCE_PUBLISH_NON_NORMALIZED_CHART_QUERY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"DAY\"}],\"metrics\":[{\"type\":\"ESTIMATED_UNIQUE_VIEWERS\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[{\"dimension\":{\"type\":\"DAY\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_ASC\"}],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20231226,\"exclusiveEnd\":20240101}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"0__SINCE_PUBLISH_HOURLY_TOTALS_QUERY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"VIDEO\"}],\"metrics\":[{\"type\":\"VIDEO_THUMBNAIL_IMPRESSIONS\"},{\"type\":\"VIEWS\"},{\"type\":\"WATCH_TIME\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[{\"dimension\":{\"type\":\"VIDEO\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_DESC\"}],\"timePeriod\":{\"unit\":\"TIME_PERIOD_UNIT_NTH_HOURS\",\"count\":106,\"nowSeconds\":\"1704015695\",\"referencePoint\":\"TIME_PERIOD_REFERENCE_POINT_SINCE_PUBLISH\",\"timePeriodType\":\"ANALYTICS_TIME_PERIOD_TYPE_SINCE_PUBLISH\",\"entity\":{\"videoId\":\"x6mcua0HOJs\"}},\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"0__SINCE_PUBLISH_HOURLY_CHART_QUERY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"NTH_HOUR\"}],\"metrics\":[{\"type\":\"VIDEO_THUMBNAIL_IMPRESSIONS\"},{\"type\":\"VIEWS\"},{\"type\":\"WATCH_TIME\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[{\"dimension\":{\"type\":\"NTH_HOUR\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_ASC\"}],\"timePeriod\":{\"unit\":\"TIME_PERIOD_UNIT_NTH_HOURS\",\"count\":106,\"nowSeconds\":\"1704015695\",\"referencePoint\":\"TIME_PERIOD_REFERENCE_POINT_SINCE_PUBLISH\",\"timePeriodType\":\"ANALYTICS_TIME_PERIOD_TYPE_SINCE_PUBLISH\",\"entity\":{\"videoId\":\"x6mcua0HOJs\"}},\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"0__SINCE_PUBLISH_HOURLY_TYPICAL_PERFORMANCE_TOTAL_QUERY\",\"value\":{\"getTypicalPerformance\":{\"query\":{\"metrics\":[{\"metric\":{\"type\":\"VIEWS\"}},{\"metric\":{\"type\":\"WATCH_TIME\"}}],\"externalChannelId\":\"UCHPoNHk_aC5LmJDDVAH4w7Q\",\"externalVideoId\":\"x6mcua0HOJs\",\"timeRange\":{\"normalizedRange\":{\"timeUnit\":\"ANALYTICS_TIME_UNIT_HOUR\",\"exclusiveEnd\":168}},\"type\":\"TYPICAL_PERFORMANCE_TYPE_NORMAL\",\"entityType\":\"TYPICAL_PERFORMANCE_ENTITY_TYPE_VIDEO\",\"currency\":\"USD\"}}}},{\"key\":\"0__SINCE_PUBLISH_HOURLY_TYPICAL_PERFORMANCE_CUMULATIVE_QUERY\",\"value\":{\"getTypicalPerformance\":{\"query\":{\"timeDimension\":{\"type\":\"NTH_HOUR\"},\"metrics\":[{\"metric\":{\"type\":\"VIEWS\"}},{\"metric\":{\"type\":\"WATCH_TIME\"}}],\"externalChannelId\":\"UCHPoNHk_aC5LmJDDVAH4w7Q\",\"externalVideoId\":\"x6mcua0HOJs\",\"timeRange\":{\"normalizedRange\":{\"timeUnit\":\"ANALYTICS_TIME_UNIT_HOUR\",\"exclusiveEnd\":168}},\"type\":\"TYPICAL_PERFORMANCE_TYPE_CUMULATIVE\",\"entityType\":\"TYPICAL_PERFORMANCE_ENTITY_TYPE_VIDEO\",\"currency\":\"USD\"}}}},{\"key\":\"0__SINCE_PUBLISH_DAILY_TOTALS_QUERY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"VIDEO\"}],\"metrics\":[{\"type\":\"VIDEO_THUMBNAIL_IMPRESSIONS_VTR\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[{\"dimension\":{\"type\":\"VIDEO\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_DESC\"}],\"timePeriod\":{\"unit\":\"TIME_PERIOD_UNIT_NTH_DAYS\",\"count\":5,\"nowSeconds\":\"1704015695\",\"referencePoint\":\"TIME_PERIOD_REFERENCE_POINT_SINCE_PUBLISH\",\"timePeriodType\":\"ANALYTICS_TIME_PERIOD_TYPE_SINCE_PUBLISH\",\"entity\":{\"videoId\":\"x6mcua0HOJs\"}},\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"0__SINCE_PUBLISH_DAILY_CHART_QUERY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"NTH_DAY\"}],\"metrics\":[{\"type\":\"VIDEO_THUMBNAIL_IMPRESSIONS_VTR\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"x6mcua0HOJs\"]}],\"orders\":[{\"dimension\":{\"type\":\"NTH_DAY\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_ASC\"}],\"timePeriod\":{\"unit\":\"TIME_PERIOD_UNIT_NTH_DAYS\",\"count\":5,\"nowSeconds\":\"1704015695\",\"referencePoint\":\"TIME_PERIOD_REFERENCE_POINT_SINCE_PUBLISH\",\"timePeriodType\":\"ANALYTICS_TIME_PERIOD_TYPE_SINCE_PUBLISH\",\"entity\":{\"videoId\":\"x6mcua0HOJs\"}},\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}}],\"connectors\":[],\"allowFailureResultNodes\":true,\"context\":{\"client\":{\"clientName\":62,\"clientVersion\":\"1.20231219.01.00\",\"hl\":\"en\",\"gl\":\"US\",\"experimentsToken\":\"\",\"utcOffsetMinutes\":-300,\"userInterfaceTheme\":\"USER_INTERFACE_THEME_DARK\",\"screenWidthPoints\":1470,\"screenHeightPoints\":353,\"screenPixelDensity\":2,\"screenDensityFloat\":2},\"request\":{\"returnLogEntry\":true,\"internalExperimentFlags\":[],\"eats\":\"AcIjWyErkOu9PGLVtJHuqIX2GB00ZxXUT5vd/qSETSYWNcxXuNqSxKJWQpHF1pPsV9oTRhgnEViNwLE60IoaqXIqplvDCKpNMw4Z/g==\",\"consistencyTokenJars\":[]},\"user\":{\"onBehalfOfUser\":\"108940515231048981095\",\"delegationContext\":{\"externalChannelId\":\"UCHPoNHk_aC5LmJDDVAH4w7Q\",\"roleType\":{\"channelRoleType\":\"CREATOR_CHANNEL_ROLE_TYPE_OWNER\"}},\"serializedDelegationContext\":\"EhhVQ0hQb05Ia19hQzVMbUpERFZBSDR3N1EqAggI\"},\"clientScreenNonce\":\"MC4yNDMyNjE0ODI5Mjk3MjAxNg..\"},\"trackingLabel\":\"web_explore_video\"}",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
}).then(response => {
  console.log(response);
});
// res = await res;
// console.log(res);
