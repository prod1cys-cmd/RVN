% Рисунок: требуемое ослабление ВАРУ и диапазон регулировки AD8367
RB = 3000; Gr = 45; R = logspace(log10(30),log10(3000),400);
A = -40*log10(R/RB);
Rgr = RB*10^(-Gr/40);
h = fig_new(16,8); hold on; box on; grid on;
semilogx(R, A, 'b'); set(gca,'XScale','log');
plot([30 3000],[Gr Gr],'r--');
plot([40 40],[0 80],'k:');
plot([Rgr Rgr],[0 Gr],'Color',[0 0.6 0],'LineStyle','-.');
Rs = R(R<=Rgr); patch([Rs fliplr(Rs)],[-40*log10(Rs/RB) Gr*ones(size(Rs))],[1 0.8 0.8],'EdgeColor','none');
text(42,73,rus(sprintf('40 м: требуется %.1f дБ',-40*log10(40/RB))));
text(Rgr*1.05,20,rus(sprintf('R_{гр} = %.0f м',Rgr)),'Color',[0 0.5 0]);
text(600,48,'диапазон регулировки 45 дБ','Color','r');
xlabel('Дальность, м'); ylabel('Ослабление ВАРУ, дБ'); ylim([0 80]); xlim([30 3000]);
legend({'закон ВАРУ 40lg(R_{В}/R)','диапазон регулировки AD8367'},'Location','northeast');
fig_save(h,'f06_varu');
