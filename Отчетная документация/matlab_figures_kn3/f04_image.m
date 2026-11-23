% Рисунок: положение рабочего, гетеродинного и зеркального каналов (fПЧ = 60 МГц)
fif = 60;
B  = {[2900 3100],[9200 9500]}; fc = [3050 9410]; nm = {'S-диапазон','X-диапазон'};
h = fig_new(16,10);
for k = 1:2
  subplot(2,1,k); hold on; box on; grid on;
  patch([B{k}(1) B{k}(2) B{k}(2) B{k}(1)],[0 0 1.3 1.3],[0.85 0.92 1],'EdgeColor','none');
  fl = fc(k)-fif; fu = fc(k)+fif;
  stem(fc(k),1,'b','filled','LineWidth',2);
  stem(fu,0.8,'Color',[0 0.6 0],'LineWidth',2);
  stem(fc(k)+2*fif,0.6,'r','LineWidth',2);
  stem(fc(k)-2*fif,0.6,'Color',[0.6 0.6 0.6],'LineStyle','--','LineWidth',1.5);
  text(fc(k),1.1,sprintf('f_c = %d',fc(k)),'HorizontalAlignment','center');
  text(fu,0.9,sprintf('f_{г} = %d',fu),'HorizontalAlignment','center','Color',[0 0.5 0]);
  text(fc(k)+2*fif,0.7,sprintf('f_{зк} = %d',fc(k)+2*fif),'HorizontalAlignment','center','Color','r');
  text(fc(k)-2*fif,0.7,sprintf('%d (при f_{г} = %d)',fc(k)-2*fif,fl),'HorizontalAlignment','center','Color',[0.4 0.4 0.4]);
  text(mean(B{k}),1.22,sprintf('полоса судовых РЛС %d–%d МГц',B{k}(1),B{k}(2)),'HorizontalAlignment','center');
  xlim([B{k}(1)-150 B{k}(2)+150]); ylim([0 1.3]); set(gca,'YTick',[]);
  xlabel('Частота, МГц'); title(nm{k});
end
fig_save(h,'f04_image');
