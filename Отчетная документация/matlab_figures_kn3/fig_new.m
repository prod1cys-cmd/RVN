function h = fig_new(w_cm, h_cm)
% Создание фигуры заданного размера (см) для вставки в отчёт
h = figure('visible','off','Color','w');
set(h,'PaperUnits','centimeters','PaperPosition',[0 0 w_cm h_cm],'PaperSize',[w_cm h_cm]);
set(h,'DefaultAxesFontSize',9,'DefaultTextFontSize',9,'DefaultLineLineWidth',1.2);
end
