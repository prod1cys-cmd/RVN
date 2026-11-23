% Рисунок: гармоники тактовых частот вблизи защищаемых частот 156–165 МГц
src = [12 25 50 100 3.125]; nm = {'12 МГц (USB)','25 МГц','50 МГц','100 МГц','3,125 МГц (SYSREF периодический)'};
h = fig_new(16,9); hold on; box on; grid on;
patch([156 165 165 156],[0.5 0.5 numel(src)+0.5 numel(src)+0.5],[1 0.9 0.7],'EdgeColor','none');
plot([156.525 156.525],[0.5 numel(src)+0.5],'r-','LineWidth',1.5);
plot([156.8 156.8],[0.5 numel(src)+0.5],'m--','LineWidth',1.5);
for k = 1:numel(src)
  m = ceil(150/src(k)):floor(170/src(k)); fh = m*src(k);
  if isempty(fh), continue; end
  plot(fh, k*ones(size(fh)), 'bo','MarkerFaceColor','b','MarkerSize',5);
  for q = 1:numel(fh)
    if fh(q)>=155 && fh(q)<=166
      text(fh(q), k+0.28, rus(sprintf('%g',fh(q))), 'HorizontalAlignment','center','FontSize',7);
    end
  end
end
set(gca,'YTick',1:numel(src),'YTickLabel',nm); ylim([0.5 numel(src)+0.5]); xlim([150 170]);
xlabel('Частота, МГц');
legend({'полоса 156–165 МГц (24 дБмкВ/м)','156,525 МГц (канал 70, ЦИВ)','156,8 МГц (канал 16)','гармоники'},'Location','southoutside','NumColumns',2);
fig_save(h,'f11_harm_vhf');
