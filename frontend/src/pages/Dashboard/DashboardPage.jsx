import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../libs/api";
import "../../styles/DashboardPage.css";

function DashboardPage() {
  const navigate = useNavigate();

  const accessToken = localStorage.getItem("accessToken");
  const isLoggedIn = Boolean(accessToken);

  const now = new Date();

  const [todayRecord, setTodayRecord] = useState(null);
  const [recentRecords, setRecentRecords] = useState([]);
  const [allRecords, setAllRecords] = useState([]);
  const [showAllRecords, setShowAllRecords] = useState(false);

  const [currentYear, setCurrentYear] = useState(now.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(now.getMonth());

  const [exerciseDays, setExerciseDays] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [monthlySummary, setMonthlySummary] = useState(null);

  const [selectedCalendarDay, setSelectedCalendarDay] = useState(null);

  const [showRecordModal, setShowRecordModal] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState("");

  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleDate, setScheduleDate] = useState("");
  const [selectedPeriod, setSelectedPeriod] = useState("오전");
  const [selectedHour, setSelectedHour] = useState(9);
  const [alarmEnabled, setAlarmEnabled] = useState(true);
  const [scheduleSubmitting, setScheduleSubmitting] = useState(false);

  const formatDuration = (seconds) => {
    if (seconds == null) {
      return "-";
    }

    const minute = Math.floor(seconds / 60);
    const second = seconds % 60;

    return `${minute}분 ${String(second).padStart(2, "0")}초`;
  };

  const formatAccuracy = (accuracy) => {
    if (accuracy == null) {
      return "-";
    }

    return `${Math.round(accuracy)}%`;
  };

  const getWeekday = (dateString) => {
    const date = new Date(`${dateString}T00:00:00`);
    const weekdays = ["일", "월", "화", "수", "목", "금", "토"];

    return weekdays[date.getDay()];
  };

  const formatRecordDate = (dateString) => {
    if (!dateString) {
      return "-";
    }

    const [, month, day] = dateString.split("-");

    return `${Number(month)}월 ${Number(day)}일 (${getWeekday(dateString)})`;
  };

  const formatToday = () => {
    const date = new Date();
    const weekdays = ["일", "월", "화", "수", "목", "금", "토"];

    return `${date.getMonth() + 1}월 ${date.getDate()}일 (${weekdays[date.getDay()]})`;
  };

  const toDateString = (year, month, day) => {
    return `${year}-${String(month + 1).padStart(2, "0")}-${String(
      day,
    ).padStart(2, "0")}`;
  };

  /* =========================
     일정 목록
  ========================= */

  const fetchSchedules = async () => {
    try {
      const response = await api.get("/api/notification/schedule");
      setSchedules(response.data || []);
    } catch (error) {
      console.error("운동 일정 조회 실패:", error);
      setSchedules([]);
    }
  };

  /* =========================
     오늘 / 최근 운동 기록
  ========================= */

  useEffect(() => {
    if (!isLoggedIn) {
      return;
    }

    const fetchDashboardRecords = async () => {
      try {
        const [todayResponse, recentResponse] = await Promise.all([
          api.get("/api/dashboard/today"),
          api.get("/api/dashboard/recent-records"),
        ]);

        setTodayRecord(todayResponse.data || null);
        setRecentRecords(recentResponse.data || []);
      } catch (error) {
        console.error("운동 기록 조회 실패:", error);
        setTodayRecord(null);
        setRecentRecords([]);
      }
    };

    fetchDashboardRecords();
    fetchSchedules();
  }, [isLoggedIn]);

  /* =========================
     캘린더 / 월간 요약
  ========================= */

  useEffect(() => {
    if (!isLoggedIn) {
      return;
    }

    const fetchMonthData = async () => {
      try {
        const [calendarResponse, summaryResponse] = await Promise.all([
          api.get("/api/dashboard/calendar", {
            params: {
              year: currentYear,
              month: currentMonth + 1,
            },
          }),

          api.get(
            `/api/dashboard/monthly-summary/${currentYear}/${currentMonth + 1}`,
          ),
        ]);

        const days = (calendarResponse.data || []).map((date) => {
          return Number(date.split("-")[2]);
        });

        setExerciseDays(days);
        setMonthlySummary(summaryResponse.data || null);
      } catch (error) {
        console.error("월별 대시보드 조회 실패:", error);
        setExerciseDays([]);
        setMonthlySummary(null);
      }
    };

    fetchMonthData();
  }, [isLoggedIn, currentYear, currentMonth]);

  /* =========================
     영상 URL 정리
  ========================= */

  useEffect(() => {
    return () => {
      if (videoPreviewUrl) {
        URL.revokeObjectURL(videoPreviewUrl);
      }
    };
  }, [videoPreviewUrl]);

  /* =========================
     기록 상세
  ========================= */

  const openRecordModal = async (recordId) => {
    try {
      const response = await api.get(`/api/dashboard/records/${recordId}`);

      const record = response.data;

      setSelectedRecord(record);
      setShowRecordModal(true);

      if (videoPreviewUrl) {
        URL.revokeObjectURL(videoPreviewUrl);
        setVideoPreviewUrl("");
      }

      if (record?.videoPath) {
        try {
          const videoResponse = await api.get(
            `/api/dashboard/records/${recordId}/video/stream`,
            {
              responseType: "blob",
            },
          );

          const url = URL.createObjectURL(videoResponse.data);
          setVideoPreviewUrl(url);
        } catch (videoError) {
          console.error("운동 영상 조회 실패:", videoError);
        }
      }
    } catch (error) {
      console.error("운동 기록 상세 조회 실패:", error);
    }
  };

  const closeRecordModal = () => {
    if (videoPreviewUrl) {
      URL.revokeObjectURL(videoPreviewUrl);
    }

    setVideoPreviewUrl("");
    setSelectedRecord(null);
    setShowRecordModal(false);
  };

  const handleVideoDownload = async () => {
    if (!selectedRecord?.sessionId) {
      return;
    }

    try {
      const response = await api.get(
        `/api/dashboard/records/${selectedRecord.sessionId}/video/download`,
        {
          responseType: "blob",
        },
      );

      const url = URL.createObjectURL(response.data);

      const link = document.createElement("a");
      link.href = url;
      link.download = `exercise-${selectedRecord.sessionId}.mp4`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("운동 영상 다운로드 실패:", error);
      alert("운동 영상을 다운로드할 수 없습니다.");
    }
  };

  /* =========================
     최근 운동 기록 더보기
  ========================= */

  const handleToggleMore = async () => {
    if (showAllRecords) {
      setShowAllRecords(false);
      return;
    }

    try {
      const response = await api.get("/api/dashboard/recent-records/all");

      setAllRecords(response.data || []);
      setShowAllRecords(true);
    } catch (error) {
      console.error("전체 운동 기록 조회 실패:", error);
    }
  };

  const visibleRecords = showAllRecords
    ? allRecords
    : recentRecords.slice(0, 5);

  /* =========================
     캘린더
  ========================= */

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentYear((prev) => prev - 1);
      setCurrentMonth(11);
    } else {
      setCurrentMonth((prev) => prev - 1);
    }

    setSelectedCalendarDay(null);
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentYear((prev) => prev + 1);
      setCurrentMonth(0);
    } else {
      setCurrentMonth((prev) => prev + 1);
    }

    setSelectedCalendarDay(null);
  };

  const handleCalendarDayClick = async (day) => {
    setSelectedCalendarDay(day);

    if (!exerciseDays.includes(day)) {
      return;
    }

    const date = toDateString(currentYear, currentMonth, day);

    try {
      const response = await api.get(`/api/dashboard/calendar/${date}`);

      if (response.data?.sessionId) {
        openRecordModal(response.data.sessionId);
      }
    } catch (error) {
      console.error("날짜별 운동 기록 조회 실패:", error);
    }
  };

  const scheduleDays = useMemo(() => {
    const prefix = `${currentYear}-${String(currentMonth + 1).padStart(
      2,
      "0",
    )}-`;

    return schedules
      .filter(
        (schedule) =>
          typeof schedule.exerciseDay === "string" &&
          schedule.exerciseDay.startsWith(prefix),
      )
      .map((schedule) => Number(schedule.exerciseDay.split("-")[2]));
  }, [schedules, currentYear, currentMonth]);

  const calendarCells = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInCurrentMonth = new Date(
      currentYear,
      currentMonth + 1,
      0,
    ).getDate();

    const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();

    return Array.from({ length: 42 }, (_, index) => {
      const dayNumber = index - firstDay + 1;

      if (dayNumber <= 0) {
        return {
          day: daysInPrevMonth + dayNumber,
          current: false,
          type: "prev",
        };
      }

      if (dayNumber > daysInCurrentMonth) {
        return {
          day: dayNumber - daysInCurrentMonth,
          current: false,
          type: "next",
        };
      }

      return {
        day: dayNumber,
        current: true,
        type: "current",
      };
    });
  }, [currentYear, currentMonth]);

  const isToday = (day) => {
    const today = new Date();

    return (
      today.getFullYear() === currentYear &&
      today.getMonth() === currentMonth &&
      today.getDate() === day
    );
  };

  /* =========================
     일정 추가
  ========================= */

  const openScheduleModal = () => {
    const today = new Date();

    let defaultDay = 1;

    if (
      today.getFullYear() === currentYear &&
      today.getMonth() === currentMonth
    ) {
      defaultDay = today.getDate();
    }

    setScheduleDate(toDateString(currentYear, currentMonth, defaultDay));

    setSelectedPeriod("오전");
    setSelectedHour(9);
    setAlarmEnabled(true);
    setShowScheduleModal(true);
  };

  const handleScheduleSubmit = async () => {
    if (!scheduleDate) {
      alert("날짜를 선택해주세요.");
      return;
    }

    let hour24 = selectedHour;

    if (selectedPeriod === "오전" && selectedHour === 12) {
      hour24 = 0;
    }

    if (selectedPeriod === "오후" && selectedHour !== 12) {
      hour24 = selectedHour + 12;
    }

    const exerciseTime = `${String(hour24).padStart(2, "0")}:00:00`;

    try {
      setScheduleSubmitting(true);

      await api.post("/api/notification/schedule", {
        exerciseDay: scheduleDate,
        exerciseTime,
        useAlert: alarmEnabled,
      });

      await fetchSchedules();

      setShowScheduleModal(false);
      alert("운동 일정이 등록되었습니다.");
    } catch (error) {
      console.error("일정 등록 실패:", error);
      alert("일정 등록에 실패했습니다.");
    } finally {
      setScheduleSubmitting(false);
    }
  };

  /* =========================
     비로그인
  ========================= */

  if (!isLoggedIn) {
    return (
      <div className="dashboardPage">
        <main className="dashboardContainer">
          <div className="dashboardHeading">
            <h1>운동 기록</h1>
            <p>최근 운동 기록과 이번 달 운동 현황을 한눈에 확인해보세요.</p>
          </div>

          <section className="dashboardLoginCard">
            <div className="dashboardLoginIcon">♙</div>

            <strong>운동 기록을 확인하려면 로그인이 필요해요.</strong>

            <p>로그인하면 운동 기록과 운동 일정을 확인할 수 있어요.</p>

            <button type="button" onClick={() => navigate("/login")}>
              로그인하기
            </button>

            <span>
              아직 회원이 아니신가요?{" "}
              <button
                type="button"
                className="signupLinkButton"
                onClick={() => navigate("/signup")}
              >
                회원가입하기
              </button>
            </span>
          </section>
        </main>
      </div>
    );
  }

  const hasAnyRecord = Boolean(todayRecord) || recentRecords.length > 0;

  return (
    <div className="dashboardPage">
      <main className="dashboardContainer">
        {/* 제목 */}
        <div className="dashboardHeading">
          <h1>운동 기록</h1>
          <p>최근 운동 기록과 이번 달 운동 현황을 한눈에 확인해보세요.</p>
        </div>

        <div className="dashboardLayout">
          {/* =========================
              왼쪽
          ========================= */}

          <div className="dashboardLeft">
            {hasAnyRecord ? (
              <>
                {/* 오늘 운동 기록 */}
                <section className="dashboardCard todayDashboardCard">
                  <div className="dashboardCardTitleRow">
                    <h2>오늘 운동 기록</h2>
                    <span>{formatToday()}</span>
                  </div>

                  {todayRecord ? (
                    <div className="todayRecordContent">
                      <div className="todayRecordStats">
                        <div className="todayRecordStat">
                          <span>운동 부위</span>
                          <strong>{todayRecord.bodyPart}</strong>
                        </div>

                        <div className="todayRecordStat">
                          <span>수행 횟수</span>
                          <strong>{todayRecord.totalCount}회</strong>
                        </div>

                        <div className="todayRecordStat">
                          <span>운동 시간</span>
                          <strong>
                            {formatDuration(todayRecord.durationSec)}
                          </strong>
                        </div>

                        <div className="todayRecordStat">
                          <span>평균 정확도</span>
                          <strong>
                            {formatAccuracy(todayRecord.accuracy)}
                          </strong>
                        </div>
                      </div>

                      <button
                        type="button"
                        className="todayRecordButton"
                        onClick={() => openRecordModal(todayRecord.sessionId)}
                      >
                        기록보기
                        <span>›</span>
                      </button>
                    </div>
                  ) : (
                    <div className="todayEmptyState">
                      <div>
                        <strong>오늘 운동 기록이 아직 없어요.</strong>
                        <p>오늘도 가볍게 운동을 시작해보세요.</p>
                      </div>

                      <button type="button" onClick={() => navigate("/")}>
                        운동 시작하기
                      </button>
                    </div>
                  )}
                </section>

                {/* 최근 운동 기록 */}
                <section className="dashboardCard recentDashboardCard">
                  <h2>최근 운동 기록</h2>

                  <div className="recentTable">
                    <div className="recentTableHeader">
                      <span>날짜</span>
                      <span>운동 부위</span>
                      <span>수행 횟수</span>
                      <span>운동 시간</span>
                      <span>평균 정확도</span>
                      <span>기록</span>
                    </div>

                    {visibleRecords.map((record) => (
                      <div className="recentTableRow" key={record.sessionId}>
                        <span>{formatRecordDate(record.exerciseDate)}</span>

                        <span>{record.bodyPart}</span>

                        <span>{record.totalCount}회</span>

                        <span>{formatDuration(record.durationSec)}</span>

                        <span>{formatAccuracy(record.accuracy)}</span>

                        <button
                          type="button"
                          className="recordArrowButton"
                          onClick={() => openRecordModal(record.sessionId)}
                          aria-label="운동 기록 상세보기"
                        >
                          ›
                        </button>
                      </div>
                    ))}
                  </div>

                  {(recentRecords.length >= 5 || showAllRecords) && (
                    <button
                      type="button"
                      className="recentMoreButton"
                      onClick={handleToggleMore}
                    >
                      {showAllRecords ? "접기 ︿" : "더보기 ﹀"}
                    </button>
                  )}
                </section>
              </>
            ) : (
              <section className="dashboardCard allRecordsEmptyCard">
                <div className="emptyRecordIcon">▣</div>

                <strong>아직 운동 기록이 없어요.</strong>

                <p>첫 운동을 시작하면 운동 기록을 여기에서 확인할 수 있어요.</p>

                <button type="button" onClick={() => navigate("/")}>
                  운동 시작하기
                </button>
              </section>
            )}
          </div>

          {/* =========================
              오른쪽
          ========================= */}

          <div className="dashboardRight">
            {/* 운동 캘린더 */}
            <section className="dashboardCard calendarDashboardCard">
              <div className="dashboardCardTitleRow calendarTitleRow">
                <h2>운동 캘린더</h2>

                <button
                  type="button"
                  className="addScheduleButton"
                  onClick={openScheduleModal}
                >
                  운동 일정 추가
                  <span>＋</span>
                </button>
              </div>

              <div className="calendarMonthHeader">
                <button
                  type="button"
                  onClick={handlePrevMonth}
                  aria-label="이전 달"
                >
                  ‹
                </button>

                <strong>
                  {currentYear}년 {currentMonth + 1}월
                </strong>

                <button
                  type="button"
                  onClick={handleNextMonth}
                  aria-label="다음 달"
                >
                  ›
                </button>
              </div>

              <div className="calendarWeekHeader">
                <span>일</span>
                <span>월</span>
                <span>화</span>
                <span>수</span>
                <span>목</span>
                <span>금</span>
                <span>토</span>
              </div>

              <div className="dashboardCalendarGrid">
                {calendarCells.map((cell, index) => {
                  const completed =
                    cell.current && exerciseDays.includes(cell.day);

                  const scheduled =
                    cell.current && scheduleDays.includes(cell.day);

                  const selected =
                    cell.current && selectedCalendarDay === cell.day;

                  return (
                    <button
                      key={`${cell.type}-${cell.day}-${index}`}
                      type="button"
                      disabled={!cell.current}
                      className={[
                        "dashboardCalendarDay",
                        !cell.current ? "outsideMonth" : "",
                        isToday(cell.day) && cell.current ? "today" : "",
                        selected ? "selected" : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      onClick={() =>
                        cell.current && handleCalendarDayClick(cell.day)
                      }
                    >
                      <span>{cell.day}</span>

                      <div className="calendarDots">
                        {completed && <i className="completedDot" />}

                        {scheduled && <i className="scheduledDot" />}
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="calendarLegend">
                <span>
                  <i className="completedDot" />
                  운동 완료
                </span>

                <span>
                  <i className="scheduledDot" />
                  운동 예정
                </span>
              </div>
            </section>

            {/* 이번 달 요약 */}
            {(monthlySummary?.totalDays ?? 0) > 0 && (
              <section className="dashboardCard monthlySummaryCard">
                <div className="dashboardCardTitleRow">
                  <h2>이번 달 요약</h2>

                  <span>
                    {currentYear}년 {currentMonth + 1}월 기준
                  </span>
                </div>

                <div className="monthlySummaryGrid">
                  <div className="monthlySummaryItem">
                    <span>총 운동 일수</span>
                    <strong>{monthlySummary?.totalDays ?? 0}일</strong>
                  </div>

                  <div className="monthlySummaryItem">
                    <span>가장 많이 운동한 부위</span>
                    <strong>{monthlySummary?.mostFrequentPart ?? "-"}</strong>
                  </div>

                  <div className="monthlySummaryItem">
                    <span>평균 운동 시간</span>
                    <strong>
                      {formatDuration(monthlySummary?.avgDurationSec)}
                    </strong>
                  </div>

                  <div className="monthlySummaryItem">
                    <span>평균 정확도</span>
                    <strong>
                      {formatAccuracy(monthlySummary?.avgAccuracy)}
                    </strong>
                  </div>
                </div>
              </section>
            )}
          </div>
        </div>
      </main>

      {/* =========================
          운동 기록 상세
      ========================= */}

      {showRecordModal && selectedRecord && (
        <div className="dashboardModalBackdrop" onMouseDown={closeRecordModal}>
          <div
            className="recordDetailModal"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="dashboardModalHeader">
              <div>
                <h2>운동 기록 상세</h2>
                <p>{formatRecordDate(selectedRecord.exerciseDate)}</p>
              </div>

              <button
                type="button"
                className="modalCloseButton"
                onClick={closeRecordModal}
              >
                ×
              </button>
            </div>

            <div className="recordDetailStats">
              <div>
                <span>운동 부위</span>
                <strong>{selectedRecord.bodyPart}</strong>
              </div>

              <div>
                <span>수행 횟수</span>
                <strong>{selectedRecord.totalCount}회</strong>
              </div>

              <div>
                <span>운동 시간</span>
                <strong>{formatDuration(selectedRecord.durationSec)}</strong>
              </div>

              <div>
                <span>평균 정확도</span>
                <strong>{formatAccuracy(selectedRecord.accuracy)}</strong>
              </div>
            </div>

            <div className="recordVideoArea">
              {videoPreviewUrl ? (
                <video
                  src={videoPreviewUrl}
                  controls
                  className="recordDetailVideo"
                />
              ) : (
                <div className="recordVideoEmpty">
                  저장된 운동 영상이 없습니다.
                </div>
              )}
            </div>

            <div className="recordModalButtons">
              <button
                type="button"
                className="recordModalCloseButton"
                onClick={closeRecordModal}
              >
                닫기
              </button>

              <button
                type="button"
                className="recordDownloadButton"
                disabled={!selectedRecord.videoPath}
                onClick={handleVideoDownload}
              >
                영상 다운로드
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================
          운동 일정 추가
      ========================= */}

      {showScheduleModal && (
        <div
          className="dashboardModalBackdrop"
          onMouseDown={() => setShowScheduleModal(false)}
        >
          <div
            className="scheduleAddModal"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="dashboardModalHeader">
              <div>
                <h2>운동 일정 추가</h2>
                <p>운동 날짜와 시간을 설정해주세요.</p>
              </div>

              <button
                type="button"
                className="modalCloseButton"
                onClick={() => setShowScheduleModal(false)}
              >
                ×
              </button>
            </div>

            <div className="scheduleForm">
              <div className="scheduleField">
                <label htmlFor="scheduleDate">날짜</label>

                <input
                  id="scheduleDate"
                  type="date"
                  value={scheduleDate}
                  onChange={(event) => setScheduleDate(event.target.value)}
                />
              </div>

              <div className="scheduleField">
                <label>운동 시간</label>

                <div className="scheduleTimeSelect">
                  <select
                    value={selectedPeriod}
                    onChange={(event) => setSelectedPeriod(event.target.value)}
                  >
                    <option value="오전">오전</option>
                    <option value="오후">오후</option>
                  </select>

                  <select
                    value={selectedHour}
                    onChange={(event) =>
                      setSelectedHour(Number(event.target.value))
                    }
                  >
                    {Array.from({ length: 12 }, (_, index) => {
                      const hour = index + 1;

                      return (
                        <option key={hour} value={hour}>
                          {String(hour).padStart(2, "0")}:00
                        </option>
                      );
                    })}
                  </select>
                </div>
              </div>

              <div className="scheduleField">
                <label>알림 받기</label>

                <div className="scheduleRadioGroup">
                  <label>
                    <input
                      type="radio"
                      name="alarm"
                      checked={alarmEnabled}
                      onChange={() => setAlarmEnabled(true)}
                    />
                    예
                  </label>

                  <label>
                    <input
                      type="radio"
                      name="alarm"
                      checked={!alarmEnabled}
                      onChange={() => setAlarmEnabled(false)}
                    />
                    아니오
                  </label>
                </div>
              </div>
            </div>

            <div className="scheduleModalButtons">
              <button
                type="button"
                className="scheduleCancelButton"
                onClick={() => setShowScheduleModal(false)}
              >
                취소
              </button>

              <button
                type="button"
                className="scheduleSubmitButton"
                disabled={scheduleSubmitting}
                onClick={handleScheduleSubmit}
              >
                {scheduleSubmitting ? "등록 중..." : "일정 추가"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;
