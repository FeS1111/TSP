\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[russian]{babel}
\usepackage{graphicx}

\title{Описание базы данных веб-приложения}
\author{}
\date{}

\begin{document}

\maketitle

\section{Описание базы данных}

База данных разработана для хранения информации о пользователях, их откликах на мероприятия, данных о мероприятиях и их категориях.

\section{Основные таблицы и их назначения}

\subsection{Таблица "Users"}
\begin{itemize}
    \item Содержит данные о пользователях.
    \item Связь с таблицей "Reactions". Пользователь может ставить реакции на мероприятие, также эта связь необходима для установления связи M:M между таблицами "Events" и "Users".
\end{itemize}

\subsection{Таблица "Categories"}
\begin{itemize}
    \item Содержит название категории и её id, нужна для определения категории мероприятия.
    \item Связь с таблицей "Events\_to\_categories": необходима для установления связи M:M между таблицами "Categories" и "Events".
\end{itemize}

\subsection{Таблица "Events"}
\begin{itemize}
    \item Содержит информацию о мероприятиях.
    \item Связь с таблицей "Reactions", "Events\_to\_categories": связь с первой таблицей необходима для установления связи M:M между таблицами "Users" и "Events", со второй для установления связи M:M между таблицами "Categories" и "Events".
\end{itemize}

\subsection{Таблица "Reactions"}
\begin{itemize}
    \item Фиксирует реакции пользователей на мероприятия.
    \item Связь с таблицами "Events" и "Users": необходима для установления связи M:M между таблицами "Events" и "Users".
\end{itemize}

\section{Физическая схема базы данных}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\textwidth]{img.png}
    \caption{Физическая схема базы данных}
    \label{fig:database_schema}
\end{figure}

\end{document}