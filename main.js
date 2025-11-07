const { Lunar } = require("./lunar");

const main = async () => {
  let today = Lunar.fromDate(new Date())
  let solarToday = today.getSolar()
  let solarDate = solarToday.getYear() + "-" + solarToday.getMonth() + "-" + solarToday.getDay()
  let lunarDate = today.getYearInChinese() + "年，" + today.getMonthInChinese() + "月，" + today.getDayInChinese() + "日"
  console.log(lunarDate, solarDate)
  let dataList = calculateBirthDay()
  console.log(dataList)
  await notify({
    title: "",
    desp: ''
  }, '')
}



const calculateBirthDay = async () => {
  let dataList = []
  let today = Lunar.fromDate(new Date())
  for (let i = 0; i < birthList.length; i++) {
    let birth = birthList[i]
    let birthDate = Lunar.fromYmd(birth.birth.split("-")[0], birth.birth.split("-")[1], birth.birth.split("-")[2])
    let lunarBirth = birthDate.getYearInChinese() + "年，" + birthDate.getMonthInChinese() + "月，" + birthDate.getDayInChinese() + "日"
    let age = today.getYear() - birthDate.getYear()

    let nextBirthDay = 0

    const birthLunarMonth = birthDate.getMonth()
    const birthLunarDay = birthDate.getDay()

    let currentYearBirth = Lunar.fromYmd(today.getYear(), birthLunarMonth, birthLunarDay)
    let currentYearSolar = currentYearBirth.getSolar() // 转换为公历

    if (currentYearSolar.toYmd() <= new Date().toISOString().split('T')[0].replace(/-/g, '')) {
      let nextYearBirth = Lunar.fromYmd(today.getYear() + 1, birthLunarMonth, birthLunarDay)
      let nextYearSolar = nextYearBirth.getSolar()

      const todayTime = new Date().getTime()
      const nextBirthTime = new Date(nextYearSolar.getYear(), nextYearSolar.getMonth() - 1, nextYearSolar.getDay()).getTime()
      nextBirthDay = Math.ceil((nextBirthTime - todayTime) / (1000 * 60 * 60 * 24))
    } else {
      const todayTime = new Date().getTime()
      const currentBirthTime = new Date(currentYearSolar.getYear(), currentYearSolar.getMonth() - 1, currentYearSolar.getDay()).getTime()
      nextBirthDay = Math.ceil((currentBirthTime - todayTime) / (1000 * 60 * 60 * 24))
    }

    dataList.push({
      name: birth.name,
      birth: lunarBirth,
      age: age,
      nextBirthDay: nextBirthDay,
    })
  }
  return dataList
}

const notify = async (contents, token) => {
  if (!token || !contents) return;
  await fetch(`https://sctapi.ftqq.com/${token}.send`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      token,
      title: contents?.title,
      desp: contents?.desp,
    }),
  });
}

main();
