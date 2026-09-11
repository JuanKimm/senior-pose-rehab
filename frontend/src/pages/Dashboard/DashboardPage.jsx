import { useEffect, useState } from "react";
import api from "../../libs/api";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "../../styles/DashboardPage.css";

function DashboardPage() {
  // 임시 로그인 상태
  // true: 대시보드 내용 확인
  // false: 비회원 blur 화면 확인
  const isLoggedIn = true;

  const [showMore, setShowMore] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDateRecord, setSelectedDateRecord] = useState(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  const [scheduleDate, setScheduleDate] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState("오전");
  const [selectedHour, setSelectedHour] = useState(9);
  const [alarmEnabled, setAlarmEnabled] = useState(true);
  const [phoneNumber, setPhoneNumber] = useState("010-1234-5678");
  const [currentYear, setCurrentYear] = useState(2026);
  const [currentMonth, setCurrentMonth] = useState(2);
  const [exerciseDays, setExerciseDays] = useState([]);

  const [monthlySummary, setMonthlySummary] = useState(null);
  const [accuracyGraph, setAccuracyGraph] = useState([]);
  const [bodyPartStats, setBodyPartStats] = useState([]);

  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        const response = await api.get("/api/notification/schedule");
        console.log("운동 일정:", response.data);
        setSchedules(response.data || []);
      } catch (error) {
        console.error("운동 일정 조회 실패:", error);
        setSchedules([]);
      }
    };

    fetchSchedules();
  }, []);

  useEffect(() => {
    const fetchBodyPartStats = async () => {
      try {
        const currentApiMonth = currentMonth + 1;

        const previousMonth = currentApiMonth === 1 ? 12 : currentApiMonth - 1;
        const previousYear =
          currentApiMonth === 1 ? currentYear - 1 : currentYear;

        const [currentResponse, previousResponse] = await Promise.all([
          api.get("/api/dashboard/stats/body-parts", {
            params: {
              year: currentYear,
              month: currentApiMonth,
            },
          }),
          api.get("/api/dashboard/stats/body-parts", {
            params: {
              year: previousYear,
              month: previousMonth,
            },
          }),
        ]);

        const currentStats = currentResponse.data;
        const previousStats = previousResponse.data;

        const bodyParts = [
          ...new Set([
            ...currentStats.map((item) => item.bodyPart),
            ...previousStats.map((item) => item.bodyPart),
          ]),
        ];

        const mergedStats = bodyParts.map((bodyPart) => {
          const current = currentStats.find(
            (item) => item.bodyPart === bodyPart,
          );

          const previous = previousStats.find(
            (item) => item.bodyPart === bodyPart,
          );

          return {
            bodyPart,
            currentCount: current?.totalCount ?? 0,
            previousCount: previous?.totalCount ?? 0,
          };
        });

        setBodyPartStats(mergedStats);
      } catch (error) {
        console.error("운동 부위 통계 조회 실패:", error);
        setBodyPartStats([]);
      }
    };

    fetchBodyPartStats();
  }, [currentYear, currentMonth]);

  useEffect(() => {
    const fetchAccuracyGraph = async () => {
      try {
        const response = await api.get("/api/dashboard/accuracy-graph");

        setAccuracyGraph(response.data);
      } catch (error) {
        console.error("정확도 그래프 조회 실패:", error);
        setAccuracyGraph([]);
      }
    };

    fetchAccuracyGraph();
  }, []);

  useEffect(() => {
    const fetchMonthlySummary = async () => {
      try {
        const response = await api.get("/api/dashboard/monthly-summary");

        setMonthlySummary(response.data);
      } catch (error) {
        console.error("이번 달 요약 조회 실패:", error);
        setMonthlySummary(null);
      }
    };

    fetchMonthlySummary();
  }, []);

  useEffect(() => {
    const fetchCalendar = async () => {
      try {
        const response = await api.get("/api/dashboard/calendar", {
          params: {
            year: currentYear,
            month: currentMonth + 1,
          },
        });

        const days = response.data.map((date) => {
          return Number(date.split("-")[2]);
        });

        setExerciseDays(days);
      } catch (error) {
        console.error("운동 캘린더 조회 실패:", error);
        setExerciseDays([]);
      }
    };

    fetchCalendar();
  }, [currentYear, currentMonth]);

  useEffect(() => {
    const fetchTodayRecord = async () => {
      try {
        const response = await api.get("/api/dashboard/today");

        if (!response.data) {
          setTodayRecord(null);
          return;
        }

        const data = response.data;

        const minutes = Math.floor(data.durationSec / 60);
        const seconds = data.durationSec % 60;

        setTodayRecord({
          id: data.sessionId,
          part: data.bodyPart,
          count: data.totalCount,
          duration: `${minutes}분 ${seconds}초`,
          accuracy: data.accuracy,
        });
      } catch (error) {
        console.error("오늘 운동 기록 조회 실패:", error);
        setTodayRecord(null);
      }
    };

    fetchTodayRecord();
  }, []);
  useEffect(() => {
    const fetchRecentRecords = async () => {
      try {
        const response = await api.get("/api/dashboard/recent-records");

        const records = response.data.map((data) => {
          const [, month, day] = data.exerciseDate.split("-");

          const minutes = Math.floor(data.durationSec / 60);
          const seconds = data.durationSec % 60;

          return {
            id: data.sessionId,
            date: `${Number(month)}월 ${Number(day)}일`,
            part: data.bodyPart,
            count: data.totalCount,
            duration: `${minutes}분 ${seconds}초`,
            accuracy: data.accuracy,
          };
        });

        setRecentRecords(records);
      } catch (error) {
        console.error("최근 운동 기록 조회 실패:", error);
        setRecentRecords([]);
      }
    };

    fetchRecentRecords();
  }, []);

  const [todayRecord, setTodayRecord] = useState(null);
  const [recentRecords, setRecentRecords] = useState([]);
  const visibleRecords = showMore ? recentRecords : recentRecords.slice(0, 3);
  const selectedSchedule = selectedDate
    ? schedules.find((schedule) => {
        const date = `${currentYear}-${String(currentMonth + 1).padStart(
          2,
          "0",
        )}-${String(selectedDate).padStart(2, "0")}`;

        return schedule.exerciseDay === date;
      })
    : null;

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentYear((prev) => prev - 1);
      setCurrentMonth(11);
    } else {
      setCurrentMonth((prev) => prev - 1);
    }

    setSelectedDate(null);
  };
  const handleDateClick = async (day) => {
    setSelectedDate(day);
    setSelectedDateRecord(null);

    const date = `${currentYear}-${String(currentMonth + 1).padStart(
      2,
      "0",
    )}-${String(day).padStart(2, "0")}`;

    try {
      const response = await api.get(`/api/dashboard/calendar/${date}`);
      setSelectedDateRecord(response.data || null);
    } catch (error) {
      console.error("선택 날짜 운동 기록 조회 실패:", error);
      setSelectedDateRecord(null);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentYear((prev) => prev + 1);
      setCurrentMonth(0);
    } else {
      setCurrentMonth((prev) => prev + 1);
    }

    setSelectedDate(null);
  };

  const handleScheduleSubmit = async () => {
    let hour24 = selectedHour;

    if (selectedPeriod === "오전" && selectedHour === 12) {
      hour24 = 0;
    }

    if (selectedPeriod === "오후" && selectedHour !== 12) {
      hour24 = selectedHour + 12;
    }

    const exerciseDay = `${currentYear}-${String(currentMonth + 1).padStart(
      2,
      "0",
    )}-${String(scheduleDate).padStart(2, "0")}`;

    const exerciseTime = `${String(hour24).padStart(2, "0")}:00:00`;

    try {
      await api.post("/api/notification/schedule", {
        exerciseDay,
        exerciseTime,
        useAlert: alarmEnabled,
      });

      const scheduleResponse = await api.get("/api/notification/schedule");
      setSchedules(scheduleResponse.data || []);

      alert("일정이 등록되었습니다.");
      setShowScheduleModal(false);
    } catch (error) {
      console.error("일정 등록 실패:", error);
      alert("일정 등록에 실패했습니다.");
    }
  };

  return (
    <div className="dashboardPage">
      {!isLoggedIn && (
        <div className="loginOverlay">
          <strong>서비스 이용을 위해</strong>
          <span>로그인이 필요합니다.</span>
        </div>
      )}

      <main
        className={`dashboardContainer ${
          !isLoggedIn ? "dashboardBlurred" : ""
        }`}
      >
        {/* 오늘 운동 기록 */}
        <section className="dashboardSection">
          <h2>오늘 운동 기록</h2>

          {todayRecord ? (
            <div className="todayRecordCard">
              <div className="todayRecordInfo">
                <p className="recordGuide">
                  오늘의 운동 상태를 한눈에 확인하세요!
                </p>

                <div className="todayStats">
                  <div className="todayStat">
                    <span>운동 부위</span>
                    <strong>{todayRecord.part}</strong>
                  </div>

                  <div className="todayStat">
                    <span>수행 횟수</span>
                    <strong>{todayRecord.count}회</strong>
                  </div>

                  <div className="todayStat">
                    <span>실행 시간</span>
                    <strong>{todayRecord.duration}</strong>
                  </div>

                  <div className="todayStat accuracyStat">
                    <span>정확도</span>
                    <strong>{todayRecord.accuracy}%</strong>
                  </div>
                </div>
              </div>

              <button type="button" className="recordVideoButton">
                기록 영상 보기
              </button>
            </div>
          ) : (
            <div className="emptyRecord">아직 오늘의 운동 기록이 없습니다.</div>
          )}
        </section>

        {/* 최근 운동 기록 */}
        <section className="dashboardSection">
          <h2>최근 운동 기록</h2>

          {recentRecords.length > 0 ? (
            <div className="recentRecordCard">
              {visibleRecords.map((record) => (
                <div className="recentRecordRow" key={record.id}>
                  <strong className="recordDate">{record.date}</strong>

                  <div className="recordItem">
                    <span>운동 부위</span>
                    <strong>{record.part}</strong>
                  </div>

                  <div className="recordItem">
                    <span>실행 횟수</span>
                    <strong>{record.count}회</strong>
                  </div>

                  <div className="recordItem">
                    <span>실행 시간</span>
                    <strong>{record.duration}</strong>
                  </div>

                  <button type="button" className="detailButton">
                    상세보기
                  </button>
                </div>
              ))}

              {recentRecords.length > 3 && (
                <button
                  type="button"
                  className="moreButton"
                  onClick={() => setShowMore((prev) => !prev)}
                >
                  {showMore ? "접기 ▲" : "더보기 ▼"}
                </button>
              )}
            </div>
          ) : (
            <div className="emptyRecord">최근 운동 기록이 없습니다.</div>
          )}
        </section>

        {/* 캘린더 */}
        <section className="dashboardSection">
          <h2>운동 캘린더</h2>

          <div className="calendarCard">
            <div className="calendarHeader">
              <button type="button" onClick={handlePrevMonth}>
                ◀
              </button>

              <strong>
                {currentYear}년 {currentMonth + 1}월
              </strong>

              <button type="button" onClick={handleNextMonth}>
                ▶
              </button>
            </div>

            <div className="calendarWeek">
              <span>일</span>
              <span>월</span>
              <span>화</span>
              <span>수</span>
              <span>목</span>
              <span>금</span>
              <span>토</span>
            </div>

            <div className="calendarGrid">
              {Array.from({ length: firstDayOfMonth }, (_, index) => (
                <div key={`empty-${index}`} className="calendarEmpty" />
              ))}

              {Array.from({ length: daysInMonth }, (_, index) => {
                const day = index + 1;

                const isMarch2026 = currentYear === 2026 && currentMonth === 2;

                const hasExercise = isMarch2026 && exerciseDays.includes(day);

                return (
                  <button
                    key={day}
                    type="button"
                    className={`calendarDay ${
                      hasExercise ? "exerciseDay" : ""
                    }`}
                    onClick={() => handleDateClick(day)}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* 이번 달 요약 */}
        <section className="dashboardSection">
          <h2>이번 달 요약</h2>

          <div className="monthlySummaryCard">
            <div className="summaryItem">
              <span>총 운동 일수</span>
              <strong>{monthlySummary?.totalDays ?? 0}일</strong>
            </div>

            <div className="summaryItem">
              <span>가장 많이 운동한 부위</span>
              <strong>{monthlySummary?.mostFrequentPart ?? "-"}</strong>
            </div>

            <div className="summaryItem">
              <span>총 운동 횟수</span>
              <strong>-</strong>
            </div>

            <div className="summaryItem">
              <span>평균 운동 시간</span>
              <strong>
                {monthlySummary?.avgDurationSec != null
                  ? `${Math.floor(monthlySummary.avgDurationSec / 60)}분 ${
                      monthlySummary.avgDurationSec % 60
                    }초`
                  : "-"}
              </strong>
            </div>
          </div>

          <div className="dashboardCharts">
            <div className="chartCard">
              <h3>날짜 별 정확도 추이</h3>

              {accuracyGraph.length > 0 ? (
                <div style={{ width: "100%", height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={accuracyGraph}>
                      <CartesianGrid strokeDasharray="3 3" />

                      <XAxis
                        dataKey="exerciseDate"
                        tickFormatter={(value) => {
                          const [, month, day] = value.split("-");
                          return `${Number(month)}/${Number(day)}`;
                        }}
                      />

                      <YAxis domain={[0, 100]} />

                      <Tooltip
                        labelFormatter={(value) => {
                          const [, month, day] = value.split("-");
                          return `${Number(month)}월 ${Number(day)}일`;
                        }}
                        formatter={(value) => [`${value}%`, "평균 정확도"]}
                      />

                      <Line
                        type="monotone"
                        dataKey="avgAccuracy"
                        stroke="#3F6F8F"
                        strokeWidth={3}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="chartEmptyState">정확도 기록이 없습니다.</div>
              )}
            </div>

            <div className="chartCard">
              <h3>월별 운동 부위 비교</h3>

              {bodyPartStats.length > 0 ? (
                <div style={{ width: "100%", height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={bodyPartStats}>
                      <CartesianGrid strokeDasharray="3 3" />

                      <XAxis dataKey="bodyPart" />

                      <YAxis allowDecimals={false} />

                      <Tooltip
                        formatter={(value) => [`${value}회`, "운동 횟수"]}
                      />

                      <Legend />

                      <Bar
                        dataKey="previousCount"
                        name={`${currentMonth === 0 ? 12 : currentMonth}월`}
                      />

                      <Bar
                        dataKey="currentCount"
                        name={`${currentMonth + 1}월`}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="chartEmptyState">
                  운동 부위 기록이 없습니다.
                </div>
              )}
            </div>
          </div>
        </section>
      </main>

      {/* 날짜 상세 팝업 */}
      {selectedDate && (
        <div className="modalBackdrop">
          <div className="dateModal">
            <h3>
              {currentMonth + 1}월 {selectedDate}일 운동 기록
            </h3>

            <div className="dateModalRow">
              <strong>운동 일정</strong>

              {selectedSchedule ? (
                <span>
                  {selectedSchedule.exerciseTime?.slice(0, 5)} ·{" "}
                  {selectedSchedule.useAlert ? "알림 ON" : "알림 OFF"}
                </span>
              ) : (
                <span>등록된 일정이 없습니다.</span>
              )}
            </div>

            <div className="dateModalRow">
              <strong>운동 기록</strong>

              {selectedDateRecord ? (
                <span>
                  {selectedDateRecord.bodyPart} 운동 ·{" "}
                  {selectedDateRecord.totalCount}회 ·{" "}
                  {Math.floor(selectedDateRecord.durationSec / 60)}분{" "}
                  {selectedDateRecord.durationSec % 60}초
                </span>
              ) : (
                <span>운동 기록이 없습니다.</span>
              )}
            </div>

            <div className="modalButtons">
              <button
                type="button"
                className="primaryModalButton"
                onClick={() => {
                  setScheduleDate(selectedDate);
                  setSelectedDate(null);
                  setShowScheduleModal(true);
                }}
              >
                일정 설정
              </button>

              <button
                type="button"
                className="secondaryModalButton"
                onClick={() => setSelectedDate(null)}
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 운동 일정 설정 팝업 */}
      {showScheduleModal && (
        <div className="modalBackdrop">
          <div className="scheduleModal">
            <h3>운동 일정 설정</h3>
            <p>날짜를 선택하고 운동 시간을 설정해주세요.</p>

            <div className="scheduleFormRow">
              <label>날짜</label>
              <input
                type="text"
                value={`${currentYear}년 ${currentMonth + 1}월 ${scheduleDate}일`}
                readOnly
              />
            </div>

            <div className="scheduleFormRow">
              <label>운동 부위</label>

              <select defaultValue="어깨">
                <option value="상체">상체 운동</option>
                <option value="어깨">어깨 운동</option>
                <option value="하체">하체 운동</option>
              </select>
            </div>

            <div className="scheduleFormRow scheduleTimeRow">
              <label>시간 선택</label>

              <div className="scheduleTimeContent">
                <div className="periodButtons">
                  <button
                    type="button"
                    className={
                      selectedPeriod === "오전" ? "selectedOption" : ""
                    }
                    onClick={() => setSelectedPeriod("오전")}
                  >
                    오전
                  </button>

                  <button
                    type="button"
                    className={
                      selectedPeriod === "오후" ? "selectedOption" : ""
                    }
                    onClick={() => setSelectedPeriod("오후")}
                  >
                    오후
                  </button>
                </div>

                <div className="hourGrid">
                  {Array.from({ length: 12 }, (_, index) => {
                    const hour = index + 1;

                    return (
                      <button
                        key={hour}
                        type="button"
                        className={
                          selectedHour === hour ? "selectedOption" : ""
                        }
                        onClick={() => setSelectedHour(hour)}
                      >
                        {hour}
                      </button>
                    );
                  })}
                </div>

                <span className="selectedTimeText">
                  선택 시간 : {selectedPeriod} {selectedHour}시
                </span>
              </div>
            </div>

            <div className="scheduleFormRow">
              <label>알림 받기</label>

              <div className="periodButtons">
                <button
                  type="button"
                  className={alarmEnabled ? "selectedOption" : ""}
                  onClick={() => setAlarmEnabled(true)}
                >
                  예
                </button>

                <button
                  type="button"
                  className={!alarmEnabled ? "selectedOption" : ""}
                  onClick={() => setAlarmEnabled(false)}
                >
                  아니오
                </button>
              </div>
            </div>

            <div className="scheduleFormRow">
              <label>알림 연락처</label>

              <input
                type="text"
                value={phoneNumber}
                disabled={!alarmEnabled}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>

            <div className="modalButtons">
              <button
                type="button"
                className="secondaryModalButton"
                onClick={() => setShowScheduleModal(false)}
              >
                취소
              </button>

              <button
                type="button"
                className="primaryModalButton"
                onClick={handleScheduleSubmit}
              >
                확인
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;
