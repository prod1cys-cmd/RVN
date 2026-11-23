% Рисунок: удаление гармоник частоты преобразования от частот бедствия СЧ/ВЧ
fd = [490 518 2174.5 2182 2187.5 4125 4177.5 4207.5 6215 6268 6312 8291 8376.5 8414.5 12290 12520 12577 16420 16695 16804.5]; % кГц
fsw = [500 1000 2000];
d = zeros(numel(fsw),numel(fd));
for i = 1:numel(fsw)
  m = max(1,round(fd/fsw(i)));
  d(i,:) = abs(fd - m*fsw(i));
end
h = fig_new(16,12);
b = barh(1:numel(fd), min(d',1000)); grid on; box on; hold on;
plot([125 125],[0 numel(fd)+1],'k:','LineWidth',1.5);
set(gca,'YTick',1:numel(fd),'YTickLabel',arrayfun(@(v) rus(sprintf('%g',v)), fd, 'UniformOutput', false),'YDir','reverse');
ylim([0 numel(fd)+1]); xlim([0 1000]); ylabel('Частота бедствия и безопасности, кГц'); xlabel('Расстояние до ближайшей гармоники, кГц (ограничено 1000)');
legend({'f_{пр} = 0,5 МГц','f_{пр} = 1 МГц','f_{пр} = 2 МГц','125 кГц'},'Location','southeast');
fprintf('min dist: %s\n', mat2str(min(d,[],2)'));
fig_save(h,'f12_dcdc');
