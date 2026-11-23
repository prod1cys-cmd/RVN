function fig_save(h, name)
% Замена десятичной точки на запятую в подписях осей и сохранение PNG
ax = findall(h,'type','axes');
for k = 1:numel(ax)
  if strcmp(get(ax(k),'Tag'),'legend'), continue; end
  for a = {'X','Y'}
    s = [a{1} 'Scale'];
    if strcmp(get(ax(k),s),'linear') && strcmp(get(ax(k),[a{1} 'TickLabelMode']),'auto')
      t = get(ax(k),[a{1} 'Tick']);
      lab = arrayfun(@(v) strrep(num2str(v),'.',','), t, 'UniformOutput', false);
      set(ax(k),[a{1} 'TickLabel'], lab);
    end
  end
end
print(h,'-dpng','-r200',[name '.png']);
close(h);
end
